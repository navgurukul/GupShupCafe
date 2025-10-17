import React, { useState, useRef } from "react";
import { ZoeSTT } from "@zoe-ng/stt";
import { ZoeTTS } from "@zoe-ng/tts";

const tts = new ZoeTTS();


const stt = new ZoeSTT();
stt.onPartial((t) => console.log("Partial:", t));
stt.onFinal((t) => console.log("Final:", t));
stt.start();

const Scenario1: React.FC = () => {
	const [processedText, setProcessedText] = useState<string>("");
	const [isTranscribing, setIsTranscribing] = useState<boolean>(false);
	const [error, setError] = useState<string>("");
	const [isProcessed, setIsProcessed] = useState<boolean>(false);
	const [extraInfo, setExtraInfo] = useState<string>(""); // New state for extra_info

	// States for TTS
	const [isTTSProcessing, setIsTTSProcessing] = useState<boolean>(false); // State for TTS processing
	const [ttsText, setTtsText] = useState<string>(""); // State for TTS input text

	const recognitionRef = useRef<SpeechRecognition | null>(null);
	const transcriptBoxRef = useRef<HTMLDivElement>(null);
	const manualStopRef = useRef<boolean>(false);
	const accumulatedRef = useRef<string>("");
	const isStartingRef = useRef<boolean>(false);
	const SpeechRecognitionClass =
		typeof window !== "undefined"
			? (window as any).SpeechRecognition ||
			(window as any).webkitSpeechRecognition
			: null;

	const startTranscription = () => {
		if (!SpeechRecognitionClass) {
			setError("Web Speech API not supported. Use Chrome or Edge.");
			return;
		}

		manualStopRef.current = false;
		isStartingRef.current = true;
		setIsTranscribing(true);
		setError("");
		accumulatedRef.current = "";
		setIsProcessed(false);
		setExtraInfo(""); // Clear extra_info on new transcription

		// Clear the contentEditable element
		if (transcriptBoxRef.current) {
			transcriptBoxRef.current.textContent = "Speak to start...";
		}

		const recognition = new SpeechRecognitionClass();
		recognition.continuous = true;
		recognition.interimResults = true;
		recognition.lang = "en-US";

		recognition.onresult = (event: SpeechRecognitionEvent) => {
			let newFinal = "";
			let newInterim = "";

			for (let i = event.resultIndex; i < event.results.length; i++) {
				const transcript = event.results[i][0].transcript;
				if (event.results[i].isFinal) {
					newFinal += transcript + " ";
				} else {
					newInterim += transcript;
				}
			}

			if (newFinal) {
				accumulatedRef.current += newFinal.trim() + " ";
			}
			console.log(
				accumulatedRef.current + newInterim,
				accumulatedRef.current,
				newInterim
			);

			// Update the contentEditable element directly instead of React state
			if (transcriptBoxRef.current) {
				transcriptBoxRef.current.textContent =
					accumulatedRef.current + newInterim;
			}
		};

		recognition.onerror = (event: SpeechRecognitionErrorEvent) => {
			// setError(`Transcription error: ${event.error}`);
			if (event.error === "no-speech") {
				if (
					!manualStopRef.current &&
					recognitionRef.current &&
					!isStartingRef.current
				) {
					isStartingRef.current = true;
					setTimeout(() => {
						if (recognitionRef.current && !manualStopRef.current) {
							try {
								recognitionRef.current.start();
							} catch (err) {
								console.log("Recognition already started or error:", err);
							}
						}
						isStartingRef.current = false;
					}, 100);
				} else {
					setIsTranscribing(false);
				}
			} else {
				setIsTranscribing(false);
			}
		};

		recognition.onend = () => {
			if (
				!manualStopRef.current &&
				recognitionRef.current &&
				!isStartingRef.current
			) {
				isStartingRef.current = true;
				setTimeout(() => {
					if (recognitionRef.current && !manualStopRef.current) {
						try {
							recognitionRef.current.start();
						} catch (err) {
							console.log("Recognition already started or error:", err);
						}
					}
					isStartingRef.current = false;
				}, 100);
			} else {
				setIsTranscribing(false);
			}
		};

		recognitionRef.current = recognition;
		isStartingRef.current = false;
		recognition.start();
	};

	const doneTranscription = () => {
		if (recognitionRef.current) {
			manualStopRef.current = true;
			isStartingRef.current = false;
			recognitionRef.current.stop();
			if (transcriptBoxRef.current) {
				transcriptBoxRef.current.contentEditable = "true";
				transcriptBoxRef.current.focus();
			}
		}
	};

	const processText = async () => {
		const transcriptBox = transcriptBoxRef.current;
		if (!transcriptBox || !transcriptBox.textContent?.trim()) {
			setError("Provide a transcript.");
			return;
		}

		try {
			setError("");
			const editedText = transcriptBox.textContent.trim();
			const response = await fetch(
				"http://localhost:8000/api/process-transcription",
				{
					method: "POST",
					headers: {
						"Content-Type": "application/json",
					},
					body: JSON.stringify({
						user_text: editedText,
						extra_info: extraInfo || null, // Pass extra_info, null if empty
					}),
				}
			);
			const data = await response.json();
			setProcessedText(data.processedText);
			setIsProcessed(true);
			if (transcriptBox) {
				transcriptBox.contentEditable = "false";
			}
		} catch (err: any) {
			setError(`Backend error: ${err.response?.data?.detail || err.message}`);
		}
	};

	return (
		<div className="scenario-page bg-white p-6 rounded-lg shadow-md">
			<h2 className="text-2xl font-semibold text-gray-800 mb-4">
				Speech to Text: User Query
			</h2>
			<p className="text-gray-600 mb-6">
				Speak your query using the mic. Click Done, edit if needed, add optional
				context, then Process.
			</p>

			<div className="transcription-section">
				<div className="flex space-x-4 mb-4">
					<button
						onClick={startTranscription}
						disabled={isTranscribing}
						className={`px-6 py-2 rounded-md font-medium text-white ${isTranscribing
							? "bg-gray-400 cursor-not-allowed"
							: "bg-blue-500 hover:bg-blue-600"
							}`}
					>
						Start Record
					</button>
					<button
						onClick={doneTranscription}
						disabled={!isTranscribing}
						className={`px-6 py-2 rounded-md font-medium text-white ${!isTranscribing
							? "bg-gray-400 cursor-not-allowed"
							: "bg-blue-500 hover:bg-blue-600"
							}`}
					>
						Done
					</button>
				</div>
				<p className="text-gray-700 font-medium">Raw Transcript (Live):</p>
				<div
					ref={transcriptBoxRef}
					id="transcriptBox"
					className="transcript-box bg-gray-50 border border-gray-300 p-4 rounded-md mt-2"
					contentEditable={isProcessed ? "false" : "false"}
					suppressContentEditableWarning={true}
				>
					{isProcessed ? processedText : "Speak to start..."}
				</div>
			</div>

			<div className="extra-info-section mt-4">
				<label htmlFor="extraInfo" className="text-gray-700 font-medium">
					Optional Context:
				</label>
				<textarea
					id="extraInfo"
					value={extraInfo}
					onChange={(e) => setExtraInfo(e.target.value)}
					placeholder="Add optional context (e.g., bot response or additional details)..."
					className="w-full p-4 border border-gray-300 rounded-md mt-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
					rows={3}
				/>
			</div>

			<button
				onClick={processText}
				disabled={!transcriptBoxRef.current?.textContent?.trim() || isProcessed}
				className={`px-6 py-2 rounded-md font-medium text-white mt-4 ${!transcriptBoxRef.current?.textContent?.trim() || isProcessed
					? "bg-gray-400 cursor-not-allowed"
					: "bg-green-500 hover:bg-green-600"
					}`}
			>
				Process Query
			</button>


			<h2 className="text-2xl font-semibold text-gray-800 mb-4 mt-8">Zoe: Text to Speech</h2>
			<p>Using the <a href="https://www.npmjs.com/package/@zoe-ng/tts" className="text-blue-500 hover:underline">@zoe-ng/tts</a> package for text-to-speech functionality.</p>
			<div>
				<textarea
					placeholder="Enter text and click 'Start Zoe TTS' to hear it spoken aloud."
					className="border border-gray-300 p-2 rounded-md mt-4 w-full"
					value={ttsText}
					onChange={(e) => setTtsText(e.target.value)}
				/>

				<button
					onClick={async () => {
						setIsTTSProcessing(true);
						try {
							await tts.speak(ttsText);
						} catch (err) {
							console.error("TTS error:", err);
							setError(`TTS error: ${err}`);
						} finally {
							setIsTTSProcessing(false);
						}
					}}
					className={`px-6 py-2 rounded-md font-medium text-white mt-2 ${
						isTTSProcessing || !ttsText.trim()
							? "bg-gray-400 cursor-not-allowed"
							: "bg-green-500 hover:bg-green-600"
					}`}
					disabled={!ttsText.trim() || isTTSProcessing}
				>
					{isTTSProcessing ? "Processing..." : "Start Zoe TTS"}
				</button>
			</div>

			{error && (
				<div className="error bg-red-100 text-red-700 p-4 rounded-md mt-4">
					{error}
				</div>
			)}
		</div>
	);
};

export default Scenario1;