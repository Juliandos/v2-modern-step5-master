import React, { useState, useEffect, useRef } from 'react';
import './index.css';
import { fetchEventSource } from "@microsoft/fetch-event-source";
import { v4 as uuidv4 } from 'uuid';

interface Message {
  message: string;
  isUser: boolean;
  sources?: string[];
}

function App() {
  const [inputValue, setInputValue] = useState("")
  const [messages, setMessages] = useState<Message[]>([]);
  const [selectedFiles, setSelectedFiles] = useState<FileList | null>(null);
  const sessionIdRef = useRef<string>(uuidv4());

  useEffect(() => {
    sessionIdRef.current = uuidv4();
  }, []);

  const setPartialMessage = (chunk: string, sources: string[] = []) => {
    setMessages(prevMessages => {
      let lastMessage = prevMessages[prevMessages.length - 1];
      if (prevMessages.length === 0 || lastMessage?.isUser) {
        // Create new AI message
        return [...prevMessages, { message: chunk, isUser: false, sources }];
      } else {
        // Update last AI message
        return [...prevMessages.slice(0, -1), {
          message: lastMessage.message + chunk,
          isUser: false,
          sources: lastMessage.sources ? [...lastMessage.sources, ...sources] : sources
        }];
      }
    })
  }

  function handleReceiveMessage(data: string) {
    let parsedData = JSON.parse(data);

    if (parsedData.chunk) {
      // Handle modern FastAPI streaming format
      const chunkData = parsedData.chunk;
      if (typeof chunkData === 'object') {
        if (chunkData.answer) {
          setPartialMessage(chunkData.answer.content || chunkData.answer);
        }
        if (chunkData.docs) {
          const sources = chunkData.docs.map((doc: any) => 
            doc.metadata?.source || doc.page_content || doc
          );
          setPartialMessage("", sources);
        }
      } else if (typeof chunkData === 'string') {
        setPartialMessage(chunkData);
      }
    }

    if (parsedData.error) {
      setPartialMessage(`Error: ${parsedData.error}`);
    }
  }

  const handleSendMessage = async (message: string) => {
    setInputValue("")

    setMessages(prevMessages => [...prevMessages, { message, isUser: true }]);

    try {
      await fetchEventSource(`http://localhost:8000/stream`, {
        method: 'POST',
        openWhenHidden: true,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: message,
          config: {
            configurable: {
              session_id: sessionIdRef.current
            }
          }
        }),
        onmessage(event) {
          if (event.data && event.data !== "[DONE]") {
            handleReceiveMessage(event.data);
          }
        },
        onerror(error) {
          console.error('Error:', error);
          setPartialMessage('Sorry, there was an error processing your request.');
        }
      })
    } catch (error) {
      console.error('Error:', error);
      setPartialMessage('Sorry, there was an error connecting to the server.');
    }
  }

  const handleKeyPress = (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      if (inputValue.trim()) {
        handleSendMessage(inputValue.trim());
      }
    }
  }

  function formatSource(source: string) {
    return source.split("/").pop() || source;
  }

  const handleUploadFiles = async () => {
    if (!selectedFiles) {
      return;
    }

    const formData = new FormData();
    Array.from(selectedFiles).forEach((file: Blob) => {
      formData.append('files', file);
    });

    try {
      const response = await fetch('http://localhost:8000/upload', {
        method: 'POST',
        body: formData,
      });
      
      if (response.ok) {
        console.log('Upload successful');
        // Clear selected files after successful upload
        setSelectedFiles(null);
        // Reset file input
        const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
        if (fileInput) fileInput.value = '';
      } else {
        console.error('Upload failed');
      }
    } catch (error) {
      console.error('Error uploading files:', error);
    }
  };

  const loadAndProcessPDFs = async () => {
    try {
      const response = await fetch('http://localhost:8000/load-and-process-pdfs', {
        method: 'POST',
      });
      if (response.ok) {
        console.log('PDFs loaded and processed successfully');
      } else {
        console.error('Failed to load and process PDFs');
      }
    } catch (error) {
      console.error('Error:', error);
    }
  };

  return (
    <div className="min-h-screen bg-white flex flex-col">
      <header className="bg-blue-100 text-gray-800 text-center p-4 shadow-sm">
        A Modern CHAT WITH YOUR PRIVATE PDFS RAG LLM App (2025)
      </header>
      <main className="flex-grow container mx-auto p-4 flex-col">
        <div className="flex-grow bg-white shadow overflow-hidden sm:rounded-lg">
          <div className="border-b border-gray-200 p-4 max-h-96 overflow-y-auto">
            {messages.length === 0 ? (
              <div className="text-gray-500 text-center py-8">
                Ask a question about your PDF documents to get started!
              </div>
            ) : (
              messages.map((msg, index) => (
                <div key={index}
                     className={`p-3 my-3 rounded-lg text-gray-800 ${msg.isUser ? "bg-blue-50 ml-8" : "bg-gray-50 mr-8"}`}>
                  {msg.message}
                  {/* Source Links */}
                  {!msg.isUser && msg.sources && msg.sources.length > 0 && (
                    <div className="text-xs mt-3">
                      <hr className="border-b mt-2 mb-3 border-gray-200"></hr>
                      <div className="text-gray-600 mb-1">Sources:</div>
                      {msg.sources.map((source, sourceIndex) => (
                        <div key={sourceIndex}>
                          <a
                            target="_blank"
                            download
                            href={`http://localhost:8000/static/${encodeURIComponent(formatSource(source))}`}
                            rel="noreferrer"
                            className="text-blue-600 hover:text-blue-800 underline"
                          >
                            {formatSource(source)}
                          </a>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
          <div className="p-4 bg-gray-50">
            <textarea
              className="form-textarea w-full p-2 border rounded text-gray-800 bg-white border-gray-300 resize-none h-auto"
              placeholder="Enter your question about the PDFs here..."
              onKeyDown={handleKeyPress}
              onChange={(e) => setInputValue(e.target.value)}
              value={inputValue}
            />
            <button
              className="mt-2 bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded transition duration-150 ease-in-out disabled:opacity-50"
              onClick={() => inputValue.trim() && handleSendMessage(inputValue.trim())}
              disabled={!inputValue.trim()}
            >
              Send
            </button>

            {/* File Upload Section */}
            <div className="mt-4 pt-4 border-t border-gray-200">
              <div className="mb-2 text-sm text-gray-700 font-medium">Upload PDF Files:</div>
              <input 
                type="file" 
                accept=".pdf" 
                multiple 
                onChange={(e) => setSelectedFiles(e.target.files)} 
                className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-medium file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
              />
              {selectedFiles && selectedFiles.length > 0 && (
                <div className="mt-2 text-xs text-gray-600">
                  Selected files: {Array.from(selectedFiles).map(file => file.name).join(', ')}
                </div>
              )}
              <div className="mt-2 flex gap-2">
                <button
                  className="bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded transition duration-150 ease-in-out disabled:opacity-50"
                  onClick={handleUploadFiles}
                  disabled={!selectedFiles || selectedFiles.length === 0}
                >
                  Upload PDFs
                </button>
                <button
                  className="bg-purple-600 hover:bg-purple-700 text-white font-bold py-2 px-4 rounded transition duration-150 ease-in-out"
                  onClick={loadAndProcessPDFs}
                >
                  Load and Process PDFs
                </button>
              </div>
            </div>
          </div>
        </div>
      </main>
      <footer className="bg-blue-100 text-gray-800 text-center p-4 text-xs border-t border-gray-200">
        Modern RAG Chat App (2025) - Built with React 19, Tailwind CSS v4 & Direct FastAPI
      </footer>
    </div>
  );
}

export default App;