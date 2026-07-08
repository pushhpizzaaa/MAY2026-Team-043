import { useState } from 'react'
import { activityCategories } from '../data/mockData.js'

export default function SubmissionModal({ onClose, onSubmit }) {
  const [category, setCategory] = useState(activityCategories[0])
  const [fileName, setFileName] = useState('')
  const [note, setNote] = useState('')

  function handleFileChange(e) {
    const file = e.target.files?.[0]
    setFileName(file ? file.name : '')
  }

  function handleSubmit(e) {
    e.preventDefault()
    onSubmit({ category, fileName, note })
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-ink/50 p-4">
      <div className="w-full max-w-md rounded-2xl bg-cream p-6 shadow-xl">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="font-display text-xl font-semibold text-ink">Submit Proof of Service</h2>
          <button
            onClick={onClose}
            className="rounded-full p-1 text-stone hover:bg-stone/10"
            aria-label="Close"
          >
            ✕
          </button>
        </div>

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div>
            <label className="mb-1 block text-sm font-semibold text-ink">Activity Category</label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="w-full rounded-lg border border-stone/25 bg-white px-3 py-2 text-sm text-ink focus:border-saffron"
            >
              {activityCategories.map((cat) => (
                <option key={cat} value={cat}>
                  {cat}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="mb-1 block text-sm font-semibold text-ink">Proof Photo</label>
            <input
              type="file"
              accept="image/*"
              onChange={handleFileChange}
              className="w-full rounded-lg border border-dashed border-stone/30 bg-white px-3 py-2 text-sm text-stone file:mr-3 file:rounded-md file:border-0 file:bg-saffron file:px-3 file:py-1 file:text-sm file:font-semibold file:text-white"
            />
            {fileName && <p className="mt-1 text-xs text-leaf-dark">Selected: {fileName}</p>}
          </div>

          <div>
            <label className="mb-1 block text-sm font-semibold text-ink">Description Note</label>
            <textarea
              value={note}
              onChange={(e) => setNote(e.target.value)}
              rows={3}
              placeholder="Briefly describe the task you performed..."
              className="w-full rounded-lg border border-stone/25 bg-white px-3 py-2 text-sm text-ink focus:border-saffron"
              required
            />
          </div>

          <div className="mt-2 flex justify-end gap-3">
            <button
              type="button"
              onClick={onClose}
              className="rounded-lg px-4 py-2 text-sm font-semibold text-stone hover:bg-stone/10"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="rounded-lg bg-leaf px-4 py-2 text-sm font-semibold text-white hover:bg-leaf-dark"
            >
              Submit for Review
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
