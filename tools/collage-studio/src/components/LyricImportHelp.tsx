// Author: Aldrin Payopay <aldrin.gdf@gmail.com> · GPL-3.0-only
import React, { useId, useRef, useState } from 'react';

const PROMPT = `Listen to the attached song and transcribe the words that are actually sung or spoken.
Keep the original language and wording. Do not rewrite, translate, complete a rhyme, or invent words during instrumental sections.
Write repeated lines out each time they occur. Put [unclear] wherever you cannot confidently hear a word.
Return only the lyrics, with one short sung phrase per line. No headings, section labels, timestamps, or Markdown.
If you cannot access or listen to the audio in this chat, say so instead of guessing.`;

const link = 'inline-flex min-h-[44px] items-center rounded-lg border border-white/15 px-3 py-2 text-sm text-amber-200 underline underline-offset-4 hover:bg-white/10 focus-visible:outline focus-visible:outline-2 focus-visible:outline-amber-300';

/** A user-directed handoff. This component never receives or uploads media. */
export function LyricImportHelp() {
  const dialogRef = useRef<HTMLDialogElement>(null);
  const triggerRef = useRef<HTMLButtonElement>(null);
  const promptRef = useRef<HTMLTextAreaElement>(null);
  const titleId = useId();
  const [notice, setNotice] = useState('');
  const copy = async () => {
    try {
      await navigator.clipboard.writeText(PROMPT);
      setNotice('Prompt copied. Paste it into your AI chat with the song attached.');
    } catch {
      promptRef.current?.focus();
      promptRef.current?.select();
      setNotice('The prompt is selected. Copy it manually, then paste it into your AI chat.');
    }
  };

  return <>
    <button ref={triggerRef} type="button" onClick={() => { setNotice(''); dialogRef.current?.showModal(); }} className="min-h-[44px] w-full rounded-lg border border-amber-300/25 bg-amber-300/5 px-3 py-2 text-left text-sm text-amber-100 hover:bg-amber-300/10 focus-visible:outline focus-visible:outline-2 focus-visible:outline-amber-300 disabled:opacity-40">
      Need lyrics? Start with your song
    </button>
    <dialog ref={dialogRef} aria-labelledby={titleId} onClose={() => triggerRef.current?.focus()} onKeyDown={event => {
      event.stopPropagation();
      // Safari's native undo can edit the last textarea behind an inert modal.
      // This guide is read-only; keep copy/select-all while owning Studio chords.
      if ((event.metaKey || event.ctrlKey) && ['z', 'y', 's', 'e', 'o'].includes(event.key.toLowerCase())) event.preventDefault();
    }} onClick={event => { if (event.target === event.currentTarget) dialogRef.current?.close(); }} className="m-auto w-[min(94vw,680px)] max-w-none max-h-[88dvh] overflow-y-auto rounded-2xl border border-white/20 bg-[#111315] p-0 text-gray-200 shadow-2xl backdrop:bg-black/75">
      <div className="sticky top-0 z-10 flex items-center justify-between gap-3 border-b border-white/10 bg-[#111315] px-4 py-3">
        <h2 id={titleId} className="text-base font-semibold text-white">Get lyrics from your song</h2>
        <button type="button" autoFocus onClick={() => dialogRef.current?.close()} className="min-h-[44px] min-w-[44px] shrink-0 rounded-lg border border-white/15 px-3 text-sm hover:bg-white/10 focus-visible:outline focus-visible:outline-2 focus-visible:outline-amber-300">Close guide</button>
      </div>
      <div className="space-y-5 p-4 text-sm leading-relaxed">
        <p>Use an AI you already have, or a free transcription tool. Already have the words written down? Paste them straight into the lyrics box.</p>
        <ol className="list-decimal space-y-3 pl-5">
          <li><strong className="text-white">Attach the song in your AI chat.</strong> If it accepts audio files, drag the song in or use its + / attachment button. Audio upload support varies by app and account.</li>
          <li><strong className="text-white">Send this prompt with the attachment.</strong> If the chat says it cannot hear the file, use one of the audio tools below.</li>
        </ol>
        <label className="block font-medium text-gray-300">Lyric transcription prompt
          <textarea ref={promptRef} readOnly value={PROMPT} rows={7} className="mt-2 min-h-[44px] w-full resize-y rounded-lg border border-white/15 bg-black/30 p-3 text-sm font-normal leading-relaxed text-gray-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-amber-300" />
        </label>
        <button type="button" onClick={() => void copy()} className="min-h-[44px] rounded-lg bg-amber-200 px-4 py-2 font-medium text-black hover:bg-amber-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-white">Copy lyric prompt</button>
        {notice && <p role="status" className="text-amber-200">{notice}</p>}
        <ol start={3} className="list-decimal space-y-3 pl-5">
          <li><strong className="text-white">Listen and correct the words.</strong> Singing, harmonies and loud music can confuse transcription. Fix every [unclear] and any invented or missed line.</li>
          <li><strong className="text-white">Bring back the lines in your take.</strong> Paste them into <em>Lyrics, one line per cue</em>, then create the evenly spaced draft. Preview each cue and adjust its start and end to the song. The draft does not automatically align the words.</li>
        </ol>
        <section aria-label="Free transcription options" className="space-y-3 border-t border-white/10 pt-4">
          <h3 className="font-semibold text-white">Free options to try</h3>
          <div className="space-y-2 rounded-xl bg-white/[0.04] p-3">
            <h4 className="font-medium text-white">Gemini — attach and ask</h4>
            <p>Sign in with Google, attach your audio, then send the prompt above. The standard allowance is up to 10 minutes of audio and 100 MB per file, with usage limits. Your file is uploaded to Google.</p>
            <div className="flex flex-wrap gap-2"><a className={link} href="https://gemini.google.com/" target="_blank" rel="noopener noreferrer">Open Gemini</a><a className={link} href="https://support.google.com/gemini/answer/14903178?hl=en" target="_blank" rel="noopener noreferrer">Current upload limits</a></div>
          </div>
          <div className="space-y-2 rounded-xl bg-white/[0.04] p-3">
            <h4 className="font-medium text-white">Whisper Web — run in your browser</h4>
            <p>Choose <strong>From file</strong>, select the song, then <strong>Transcribe</strong>. The model downloads first and processes the audio on your device. Use <strong>Export TXT</strong>, correct the words and break them into short lyric lines before pasting here. A laptop is a better starting point for long recordings; the first run can be slow.</p>
            <div className="flex flex-wrap gap-2"><a className={link} href="https://huggingface.co/spaces/Xenova/whisper-web" target="_blank" rel="noopener noreferrer">Open Whisper Web</a><a className={link} href="https://github.com/xenova/whisper-web" target="_blank" rel="noopener noreferrer">Open-source project</a></div>
          </div>
          <div className="space-y-2 rounded-xl bg-white/[0.04] p-3">
            <h4 className="font-medium text-white">Apple Silicon — local setup</h4>
            <p>For an M-series Mac, MLX Whisper is a free open-source route with setup required. Download the package and a model, transcribe on your Mac, then bring the TXT words or SRT file back here. Check the words and timing before using them. This is an external tool, not a Studio installer.</p>
            <a className={link} href="https://github.com/ml-explore/mlx-examples/tree/main/whisper" target="_blank" rel="noopener noreferrer">Apple Silicon setup guide</a>
          </div>
          <p className="text-xs text-gray-400">Links checked September 5, 2026. These open separate tools; Studio does not send your song to them. Availability and limits can change.</p>
        </section>
      </div>
    </dialog>
  </>;
}
