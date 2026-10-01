import { useState } from 'react';
import { UploadCloud } from 'lucide-react';

const API_BASE = "https://fin-health-system.onrender.com"; // Change to your live URL or localhost
const API_KEY = "dev-secret-key-change-later";

export default function UploadScreen() {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState('');

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) return;

    setStatus('Uploading...');
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${API_BASE}/upload-transactions`, {
        method: 'POST',
        headers: { "X-API-Key": API_KEY },
        body: formData,
      });
      
      const data = await response.json();
      if (response.ok) {
        setStatus(`Success: ${data.message}`);
      } else {
        setStatus(`Error: ${data.detail}`);
      }
    } catch (err) {
      setStatus('Failed to connect to server.');
    }
  };

  return (
    <div className="max-w-3xl mx-auto">
      <h1 className="text-3xl font-bold text-white mb-2">Data Ingestion</h1>
      <p className="text-slate-400 mb-8">Upload your latest Excel or CSV transaction ledger to update the analytics engine.</p>

      <div className="bg-cardBg border border-slate-700 rounded-xl p-8 text-center">
        <UploadCloud size={48} className="mx-auto text-accentYellow mb-4" />
        <h3 className="text-xl font-medium text-white mb-2">Select a file to upload</h3>
        
        <form onSubmit={handleUpload} className="mt-6 flex flex-col items-center gap-4">
          <input 
            type="file" 
            accept=".csv, .xlsx" 
            onChange={(e) => setFile(e.target.files[0])}
            className="block w-full max-w-sm text-sm text-slate-400 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-accentYellow file:text-black hover:file:bg-yellow-400 cursor-pointer"
          />
          <button type="submit" disabled={!file} className="px-8 py-2 bg-accentYellow text-black font-bold rounded-lg disabled:opacity-50 mt-4">
            Process Data
          </button>
        </form>
        
        {status && <p className="mt-6 text-accentYellow font-medium">{status}</p>}
      </div>
    </div>
  );
}