
import { useEffect, useState } from "react";
import { HardDriveDownload } from "lucide-react";
import { processVideo } from "../services/api.js";
import { useAppContext } from "../context/AppContext.jsx";
import ButtonArrowDown from "../components/ui/ButtonArrowDown.jsx";
import DotLoader from "../components/ui/DotLoader.jsx";

export default function UploadPage() {
	const { scriptResult, setErrorMessage, setIsBusy, isBusy } = useAppContext();
	const [videoFile, setVideoFile] = useState(null);
	const [scriptText, setScriptText] = useState(scriptResult?.script || "");
	const [response, setResponse] = useState(null);

	useEffect(() => {
		setScriptText(scriptResult?.script || "");
	}, [scriptResult]);

	const handleSubmit = async (event) => {
		event.preventDefault();
		if (!videoFile) {
			setErrorMessage("Attach a video file before processing.");
			return;
		}

		setIsBusy(true);
		setErrorMessage("");

		const formData = new FormData();
		formData.append("video", videoFile);
		formData.append("script", scriptText || "");

		try {
			const { data } = await processVideo(formData);
			setResponse(data);
		} catch (error) {
			console.error("Upload failed", error);
			const detail = error.response?.data?.detail;
			setErrorMessage(detail || "Unable to process the video. Check the backend log.");
			setResponse(null);
		} finally {
			setIsBusy(false);
		}
	};

	return (
		<section className="card">
			<header className="card__header">
				<h2>ShareBlast: Video Processing</h2>
				<p>Drop raw footage and Nexus spins platform-ready shorts with metadata preserved.</p>
			</header>

			<form onSubmit={handleSubmit} className="field-group" style={{ marginTop: "1.5rem" }}>
				<label htmlFor="video" className="upload-dropzone">
					<HardDriveDownload size={20} aria-hidden="true" />
					<span>
						{videoFile?.name || "Drop your .mp4 or .mov here"}
					</span>
					<input
						id="video"
						type="file"
						accept="video/*"
						onChange={(event) => setVideoFile(event.target.files?.[0] || null)}
					/>
				</label>

				<label htmlFor="script">Script (optional)</label>
				<textarea
					id="script"
					className="script-output"
					value={scriptText}
					onChange={(event) => setScriptText(event.target.value)}
					placeholder="Paste the Nexus script output here"
				/>

				<ButtonArrowDown type="submit" disabled={isBusy}>
					{isBusy ? "Processing footage" : "Clip & prep shorts"}
				</ButtonArrowDown>
			</form>

			{isBusy ? <DotLoader label="Nexus slicing scenes" /> : null}

			{response?.shorts?.length ? (
				<div style={{ marginTop: "2rem" }}>
					<h3>Generated shorts</h3>
					<div className="grid">
						{response.shorts.map((short) => (
							<article key={short.id} className="trend-card">
								<strong>{short.id}</strong>
								<p>Duration: {short.duration}s</p>
								<p>Video URL: {short.videoUrl}</p>
								<p>Views: {short.views}</p>
							</article>
						))}
					</div>
				</div>
			) : null}

			{response?.message ? (
				<p style={{ marginTop: "1.5rem", color: "var(--text-secondary)" }}>
					{response.message}
				</p>
			) : null}
		</section>
	);
}
