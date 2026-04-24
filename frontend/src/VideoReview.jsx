import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Play, ArrowLeft, Save } from 'lucide-react';

function VideoReview() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const [script, setScript] = useState('');
  const [youtubeTitle, setYoutubeTitle] = useState('');
  const [youtubeDesc, setYoutubeDesc] = useState('');
  const [narratorGender, setNarratorGender] = useState('male');

  useEffect(() => {
    fetchProject();
  }, [id]);

  const fetchProject = async () => {
    try {
      const res = await axios.get(`/api/projects/${id}`);
      setProject(res.data);
      setScript(res.data.script || '');
      setYoutubeTitle(res.data.youtube_title || res.data.title || '');
      setYoutubeDesc(res.data.youtube_desc || '');
      setNarratorGender(res.data.narrator_gender || 'male');
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await axios.put(`/api/projects/${id}/draft`, {
        script,
        youtube_title: youtubeTitle,
        youtube_desc: youtubeDesc,
        narrator_gender: narratorGender,
      });
      alert('Draft saved successfully');
    } catch (err) {
      console.error(err);
      alert('Failed to save draft');
    } finally {
      setSaving(false);
    }
  };

  const handleApprove = async () => {
    try {
      await axios.put(`/api/projects/${id}/draft`, {
        script,
        youtube_title: youtubeTitle,
        youtube_desc: youtubeDesc,
        narrator_gender: narratorGender,
      });
      await axios.post(`/api/projects/${id}/approve`);
      navigate('/');
    } catch (err) {
      console.error(err);
      alert('Failed to approve project');
    }
  };

  if (loading) return <div className="p-8 text-center text-on-surface-variant">Loading...</div>;
  if (!project) return <div className="p-8 text-center text-tertiary">Project not found</div>;

  return (
    <div className="max-w-5xl mx-auto">
      <button
        onClick={() => navigate('/')}
        className="mb-8 inline-flex items-center text-secondary-container hover:text-on-surface font-bold transition-colors"
      >
        <ArrowLeft className="w-5 h-5 mr-2" /> Back to Dashboard
      </button>

      <div className="rounded-3xl border border-outline-variant/40 bg-surface-container-lowest/95 shadow-glow p-8 md:p-10">
        <h1 className="text-4xl font-manrope font-extrabold mb-8 tracking-tight">{project.title}</h1>

        <div className="space-y-6">
          <div>
            <label className="block text-sm font-bold text-on-surface mb-2 tracking-wide">VIDEO SCRIPT</label>
            <textarea
              className="w-full h-64 p-4 rounded-xl bg-surface-container-high/80 text-on-surface border border-outline-variant/40 focus:outline-none focus:ring-2 focus:ring-secondary-container/50 resize-none"
              value={script}
              onChange={(e) => setScript(e.target.value)}
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-bold text-on-surface mb-2 tracking-wide">YOUTUBE TITLE</label>
              <input
                type="text"
                className="w-full p-4 rounded-xl bg-surface-container-high/80 text-on-surface border border-outline-variant/40 focus:outline-none focus:ring-2 focus:ring-secondary-container/50"
                value={youtubeTitle}
                onChange={(e) => setYoutubeTitle(e.target.value)}
              />
            </div>
            <div>
              <label className="block text-sm font-bold text-on-surface mb-2 tracking-wide">NARRATOR VOICE</label>
              <select
                className="w-full p-4 rounded-xl bg-surface-container-high/80 text-on-surface border border-outline-variant/40 focus:outline-none focus:ring-2 focus:ring-secondary-container/50"
                value={narratorGender}
                onChange={(e) => setNarratorGender(e.target.value)}
              >
                <option value="male">Male</option>
                <option value="female">Female</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-bold text-on-surface mb-2 tracking-wide">YOUTUBE DESCRIPTION</label>
            <textarea
              className="w-full h-32 p-4 rounded-xl bg-surface-container-high/80 text-on-surface border border-outline-variant/40 focus:outline-none focus:ring-2 focus:ring-secondary-container/50 resize-none"
              value={youtubeDesc}
              onChange={(e) => setYoutubeDesc(e.target.value)}
            />
          </div>

          <div className="pt-8 flex flex-wrap justify-end gap-4 border-t border-outline-variant/40">
            <button
              onClick={handleSave}
              disabled={saving}
              className="px-6 py-3 rounded-full font-bold text-on-surface border border-outline-variant hover:bg-surface-container-low transition-colors inline-flex items-center"
            >
              <Save className="w-5 h-5 mr-2" /> Save Draft
            </button>
            <button
              onClick={handleApprove}
              className="px-8 py-3 rounded-full font-bold text-on-primary bg-gradient-to-r from-primary-dim to-primary shadow-sm hover:brightness-110 transition inline-flex items-center"
            >
              Approve & Generate <Play className="w-5 h-5 ml-2" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default VideoReview;
