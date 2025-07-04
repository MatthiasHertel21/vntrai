"""
Task Executor
Handles task execution logic for both AI and tool tasks
"""

import json
from app.utils.data_manager import agent_run_manager, tools_manager
from .api_utils import log_error, log_info
from .openai_client import OpenAIClient
from .prompt_builder import build_context_prompt, render_response_content
from .thread_management import get_thread_lock


class TaskExecutor:
    """Handles execution of different task types"""
    
    def __init__(self, run_uuid, task_uuid, task_def, task_inputs, agent, request_method):
        self.run_uuid = run_uuid
        self.task_uuid = task_uuid
        self.task_def = task_def
        self.task_inputs = task_inputs
        self.agent = agent
        self.request_method = request_method
    
    def execute(self):
        """Execute the task based on its type"""
        try:
            # Update task status to running
            agent_run_manager.set_task_status(self.run_uuid, self.task_uuid, 'running')
            
            # Generate initial HTML
            start_html = '<div class="task-execution-output">'
            yield f"data: {json.dumps({'type': 'html_chunk', 'content': start_html})}\n\n"
            
            # Execute based on task type
            if self.task_def.get('type') == 'ai':
                yield from self._execute_ai_task()
            else:
                yield from self._execute_tool_task()
            
            # Close the main container
            end_html = '</div>'
            yield f"data: {json.dumps({'type': 'html_chunk', 'content': end_html})}\n\n"
            
            # Save task inputs
            agent_run_manager.set_task_inputs(self.run_uuid, self.task_uuid, self.task_inputs)
            
            # Signal completion
            yield f"data: {json.dumps({'type': 'complete'})}\n\n"
            
        except Exception as e:
            log_error(f"Error in task execution: {str(e)}")
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
            # Set task status to error
            try:
                agent_run_manager.set_task_status(self.run_uuid, self.task_uuid, 'error', str(e))
            except:
                pass
    
    def _execute_ai_task(self):
        """Execute AI task with OpenAI Assistant integration"""
        # Create or get user session for this task
        task_state = agent_run_manager.get_task_state(self.run_uuid, self.task_uuid)
        thread_id = task_state.get('user_session_id') if task_state else None
        
        # Acquire thread lock to prevent concurrent access to the same OpenAI thread
        if thread_id:
            thread_lock = get_thread_lock(thread_id)
            log_info(f"Acquiring lock for thread {thread_id}")
            if not thread_lock.acquire(timeout=30):  # 30 second timeout
                error_html = '<div class="error-section mb-6"><div class="bg-red-50 p-4 rounded-lg"><div class="text-red-700 font-medium">Error: Thread is busy with another request. Please wait and try again.</div></div></div>'
                yield f"data: {json.dumps({'type': 'html_chunk', 'content': error_html})}\n\n"
                agent_run_manager.set_task_status(self.run_uuid, self.task_uuid, 'error', 'Thread busy')
                return
            log_info(f"Acquired lock for thread {thread_id}")
        else:
            thread_lock = None
        
        try:
            # Get OpenAI configuration
            openai_client, error_html = self._get_openai_client()
            if not openai_client:
                yield f"data: {json.dumps({'type': 'html_chunk', 'content': error_html})}\n\n"
                return
            
            # Get assistant ID
            assistant_id = self.agent.get('assistant_id')
            if not assistant_id:
                error_html = '<div class="error-section mb-6"><div class="bg-red-50 p-4 rounded-lg"><div class="text-red-700 font-medium">Error: No Assistant ID found for this agent</div></div></div>'
                yield f"data: {json.dumps({'type': 'html_chunk', 'content': error_html})}\n\n"
                agent_run_manager.set_task_status(self.run_uuid, self.task_uuid, 'error', 'No Assistant ID')
                return
            
            # Create thread if not exists
            if not thread_id:
                thread_id = yield from self._create_or_get_thread(openai_client)
                if not thread_id:
                    return  # Error already handled
                
                # Now we have a thread_id, acquire the lock
                thread_lock = get_thread_lock(thread_id)
                log_info(f"Acquiring lock for newly created thread {thread_id}")
                if not thread_lock.acquire(timeout=30):  # 30 second timeout
                    error_html = '<div class="error-section mb-6"><div class="bg-red-50 p-4 rounded-lg"><div class="text-red-700 font-medium">Error: Unable to acquire lock for new thread. Please try again.</div></div></div>'
                    yield f"data: {json.dumps({'type': 'html_chunk', 'content': error_html})}\n\n"
                    agent_run_manager.set_task_status(self.run_uuid, self.task_uuid, 'error', 'Lock acquisition failed')
                    return
                log_info(f"Acquired lock for newly created thread {thread_id}")
            
            # Execute the OpenAI prompt
            yield from self._execute_openai_prompt(openai_client, thread_id, assistant_id)
            
        except Exception as ai_error:
            error_html = f'<div class="error-section mb-6"><div class="bg-red-50 p-4 rounded-lg"><div class="text-red-700 font-medium">Exception: {str(ai_error)}</div></div></div>'
            yield f"data: {json.dumps({'type': 'html_chunk', 'content': error_html})}\n\n"
            agent_run_manager.set_task_status(self.run_uuid, self.task_uuid, 'error', str(ai_error))
        
        finally:
            # Always release the thread lock if we acquired one
            if thread_lock:
                log_info(f"Releasing lock for thread {thread_id}")
                thread_lock.release()
    
    def _execute_tool_task(self):
        """Execute tool task (simple completion)"""
        # For tool tasks, just mark as completed without additional output
        agent_run_manager.set_task_status(self.run_uuid, self.task_uuid, 'completed')
    
    def _get_openai_client(self):
        """Get configured OpenAI client or return error"""
        try:
            # Get API key from the agent's AI assistant tool configuration
            ai_assistant_tool = self.agent.get('ai_assistant_tool', '')
            log_info(f"Agent AI assistant tool: {ai_assistant_tool}")
            
            if ai_assistant_tool.startswith('tool:'):
                tool_id = ai_assistant_tool.replace('tool:', '')
                log_info(f"Loading tool with ID: {tool_id}")
                tool = tools_manager.load(tool_id)
                if tool:
                    tool_config = tool.get('config', {})
                    api_key = tool_config.get('openai_api_key')
                    log_info(f"API key found: {'Yes' if api_key and api_key != 'test-key-placeholder' else 'No'}")
                    
                    if not api_key or api_key == 'test-key-placeholder':
                        error_html = '<div class="error-section mb-6"><div class="bg-red-50 p-4 rounded-lg"><div class="text-red-700 font-medium">Error: No valid OpenAI API key found in tool configuration</div></div></div>'
                        agent_run_manager.set_task_status(self.run_uuid, self.task_uuid, 'error', 'No valid OpenAI API key')
                        return None, error_html
                    
                    return OpenAIClient(api_key), None
                else:
                    error_html = '<div class="error-section mb-6"><div class="bg-red-50 p-4 rounded-lg"><div class="text-red-700 font-medium">Error: AI assistant tool not found</div></div></div>'
                    agent_run_manager.set_task_status(self.run_uuid, self.task_uuid, 'error', 'AI assistant tool not found')
                    return None, error_html
            else:
                error_html = '<div class="error-section mb-6"><div class="bg-red-50 p-4 rounded-lg"><div class="text-red-700 font-medium">Error: No AI assistant tool configured</div></div></div>'
                agent_run_manager.set_task_status(self.run_uuid, self.task_uuid, 'error', 'No AI assistant tool configured')
                return None, error_html
                
        except Exception as e:
            error_html = f'<div class="error-section mb-6"><div class="bg-red-50 p-4 rounded-lg"><div class="text-red-700 font-medium">Error configuring OpenAI client: {str(e)}</div></div></div>'
            agent_run_manager.set_task_status(self.run_uuid, self.task_uuid, 'error', f'OpenAI configuration failed: {str(e)}')
            return None, error_html
    
    def _create_or_get_thread(self, openai_client):
        """Create a new OpenAI thread or return existing one"""
        success, thread_id, error_msg = openai_client.create_thread()
        
        if success:
            # Save thread ID to agent run
            agent_run_manager.update_task_state(self.run_uuid, self.task_uuid, {'user_session_id': thread_id})
            return thread_id
        else:
            error_html = f'<div class="error-section mb-6"><div class="bg-red-50 p-4 rounded-lg"><div class="text-red-700 font-medium">Error creating session: {error_msg}</div></div></div>'
            yield f"data: {json.dumps({'type': 'html_chunk', 'content': error_html})}\n\n"
            agent_run_manager.set_task_status(self.run_uuid, self.task_uuid, 'error', f'Session creation failed: {error_msg}')
            return None
    
    def _execute_openai_prompt(self, openai_client, thread_id, assistant_id):
        """Execute the context prompt via OpenAI Assistant API"""
        # Load agent run to get preferences
        agent_run = agent_run_manager.load(self.run_uuid)
        
        # Build context prompt with agent run data for language preference
        context_prompt = build_context_prompt(self.task_def, self.task_inputs, self.agent, agent_run)
        
        # Note: Context prompt output removed per backlog item - no longer displaying prompt to user
        
        # Add message to thread
        success, error_msg = openai_client.add_message_to_thread(thread_id, context_prompt)
        if not success:
            # Check if this is the specific "thread has active run" error
            if "has an active run" in error_msg:
                error_html = f'<div class="error-section mb-6"><div class="bg-red-50 p-4 rounded-lg"><div class="text-red-700 font-medium">Thread Synchronization Error: The OpenAI thread still has an active run despite our cleanup attempts.<br><br>This indicates a race condition or API timing issue. Please:<br>1. Wait 2-3 minutes for any pending operations to complete<br>2. Try the request again<br><br>Technical details: {error_msg}</div></div></div>'
            else:
                error_html = f'<div class="error-section mb-6"><div class="bg-red-50 p-4 rounded-lg"><div class="text-red-700 font-medium">Error: {error_msg}</div></div></div>'
            
            yield f"data: {json.dumps({'type': 'html_chunk', 'content': error_html})}\n\n"
            agent_run_manager.set_task_status(self.run_uuid, self.task_uuid, 'error', error_msg)
            return
        
        # Create streaming run
        stream_response = openai_client.create_streaming_run(thread_id, assistant_id)
        if not stream_response:
            error_html = f'<div class="error-section mb-6"><div class="bg-red-50 p-4 rounded-lg"><div class="text-red-700 font-medium">Error: Failed to create streaming run</div></div></div>'
            yield f"data: {json.dumps({'type': 'html_chunk', 'content': error_html})}\n\n"
            agent_run_manager.set_task_status(self.run_uuid, self.task_uuid, 'error', 'Failed to create streaming run')
            return
        
        # Process streaming response
        yield from self._handle_streaming_response(stream_response, openai_client, thread_id, assistant_id)
    
    def _handle_completion(self, openai_client, thread_id, context_prompt, assistant_id):
        """Handle successful completion of OpenAI Assistant run"""
        success, response_content, error_msg = openai_client.get_thread_messages(thread_id)
        
        if success:
            # Render response based on task output rendering type
            # Check both old (output.type) and new (output_rendering) field structures
            output_rendering = self.task_def.get('output_rendering', '')
            log_info(f"Task definition output_rendering: {output_rendering}")
            log_info(f"Task definition keys: {list(self.task_def.keys())}")
            
            if not output_rendering:
                # Fallback to old structure
                output_config = self.task_def.get('output', {})
                output_rendering = output_config.get('type', 'text')
                log_info(f"Fallback output_rendering from output.type: {output_rendering}")
                log_info(f"Output config: {output_config}")
            
            log_info(f"Final output_rendering used: {output_rendering}")
            rendered_content = render_response_content(response_content, output_rendering)
            log_info(f"Rendered content length: {len(rendered_content)}")
            log_info(f"Raw response content: {response_content[:200]}...")
            
            # Display result directly without extra container
            yield f"data: {json.dumps({'type': 'html_chunk', 'content': rendered_content})}\n\n"
            
            # Save results to agent run
            results_data = {
                'html_output': rendered_content,
                'raw_response': response_content,
                'thread_id': thread_id,
                'assistant_id': assistant_id
            }
            agent_run_manager.set_task_results(self.run_uuid, self.task_uuid, results_data)
            agent_run_manager.set_task_status(self.run_uuid, self.task_uuid, 'completed')
            
        else:
            error_html = f'<div class="error-section mb-6"><div class="bg-red-50 p-4 rounded-lg"><div class="text-red-700 font-medium">Error: {error_msg}</div></div></div>'
            yield f"data: {json.dumps({'type': 'html_chunk', 'content': error_html})}\n\n"
            agent_run_manager.set_task_status(self.run_uuid, self.task_uuid, 'error', error_msg)
    
    def _handle_streaming_response(self, stream_response, openai_client, thread_id, assistant_id):
        """Handle streaming response from OpenAI Assistant API v2"""
        try:
            agent_run = agent_run_manager.load(self.run_uuid)
            output_rendering = self.task_def.get('output_rendering', '')
            if not output_rendering:
                output_config = self.task_def.get('output', {})
                output_rendering = output_config.get('type', 'text')
            
            accumulated_content = ""
            has_content = False
            last_render_length = 0  # Track when we last rendered to avoid too frequent updates
            
            # Process the streaming response event by event
            for event in stream_response:
                if event.data:
                    log_info(f"Received streaming event: {event.event}")
                    
                    # Handle different event types  
                    if event.event == 'thread.message.delta' and hasattr(event, 'data'):
                        # This is where the actual content comes from
                        delta = event.data.delta
                        
                        if hasattr(delta, 'content'):
                            for content_item in delta.content:
                                if content_item.type == 'text' and hasattr(content_item, 'text'):
                                    text_value = content_item.text.value
                                    
                                    if text_value:
                                        log_info(f"Received text delta: {text_value[:50]}...")
                                        accumulated_content += text_value
                                        has_content = True
                                        
                                        # Stream the content - render every ~100 characters or on sentence boundaries
                                        should_render = (
                                            len(accumulated_content) - last_render_length >= 100 or
                                            text_value.endswith('.') or 
                                            text_value.endswith('!') or 
                                            text_value.endswith('?') or
                                            text_value.endswith('\n\n')
                                        )
                                        
                                        if should_render and output_rendering in ['markdown', 'markup']:
                                            # Render accumulated content so far and send as special event type
                                            try:
                                                temp_rendered = render_response_content(accumulated_content, output_rendering)
                                                # Send rendered content as special markdown_update event
                                                event_data = {
                                                    'type': 'markdown_update', 
                                                    'content': temp_rendered, 
                                                    'container_id': f'streaming-content-{self.task_uuid}'
                                                }
                                                yield f"data: {json.dumps(event_data)}\n\n"
                                                last_render_length = len(accumulated_content)
                                            except Exception as render_error:
                                                log_error(f"Markdown rendering error during streaming: {render_error}")
                                                # Send raw text as fallback
                                                import html
                                                escaped_text = html.escape(text_value)
                                                event_data = {'type': 'text_chunk', 'content': escaped_text}
                                                yield f"data: {json.dumps(event_data)}\n\n"
                                        
                                        elif output_rendering not in ['markdown', 'markup']:
                                            # For text output, escape and send immediately as text chunk
                                            import html
                                            escaped_text = html.escape(text_value)
                                            event_data = {'type': 'text_chunk', 'content': escaped_text}
                                            yield f"data: {json.dumps(event_data)}\n\n"
                    
                    elif event.event == 'thread.run.completed':
                        log_info("Run completed - processing final content")
                        break
                        
                else:
                    log_info(f"Received streaming event: {event.event}")
            
            # Process final accumulated content
            if has_content and accumulated_content:
                log_info(f"Processing final content: {len(accumulated_content)} characters")
                
                # Render the complete content based on output type
                rendered_content = render_response_content(accumulated_content, output_rendering)
                
                # Send final rendered content
                event_data = {
                    'type': 'final_content', 
                    'content': rendered_content, 
                    'container_id': f'streaming-content-{self.task_uuid}'
                }
                yield f"data: {json.dumps(event_data)}\n\n"
                
                # Save results to agent run
                results_data = {
                    'html_output': rendered_content,
                    'raw_response': accumulated_content,
                    'thread_id': thread_id,
                    'assistant_id': assistant_id
                }
                agent_run_manager.set_task_results(self.run_uuid, self.task_uuid, results_data)
                agent_run_manager.set_task_status(self.run_uuid, self.task_uuid, 'completed')
                
            else:
                # No content received
                log_error("No response received from AI")
                agent_run_manager.set_task_status(self.run_uuid, self.task_uuid, 'error', 'No response received')
                error_html = '<div class="error-section mb-6"><div class="bg-red-50 p-4 rounded-lg"><div class="text-red-700 font-medium">No response received from AI</div></div></div>'
                yield f"data: {json.dumps({'type': 'html_chunk', 'content': error_html})}\n\n"
                
        except Exception as e:
            log_error(f"Error in streaming response handler: {str(e)}")
            agent_run_manager.set_task_status(self.run_uuid, self.task_uuid, 'error', str(e))
            error_html = f'<div class="error-section mb-6"><div class="bg-red-50 p-4 rounded-lg"><div class="text-red-700 font-medium">Streaming error: {str(e)}</div></div></div>'
            yield f"data: {json.dumps({'type': 'html_chunk', 'content': error_html})}\n\n"
