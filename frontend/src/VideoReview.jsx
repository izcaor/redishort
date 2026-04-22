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
      // Save first
      await axios.put(`/api/projects/${id}/draft`, {
        script,
        youtube_title: youtubeTitle,
        youtube_desc: youtubeDesc,
        narrator_gender: narratorGender,
      });
      // Then approve
      await axios.post(`/api/projects/${id}/approve`);
      navigate('/');
    } catch (err) {
      console.error(err);
      alert('Failed to approve project');
    }
  };

  if (loading) return <div className="p-8 text-center">Loading...</div>;
  if (!project) return <div className="p-8 text-center text-tertiary">Project not found</div>;

  return (
    <div className="max-w-4xl mx-auto">
      <button
        onClick={() => navigate('/')}
        className="mb-8 inline-flex items-center text-primary hover:text-primary-dim font-bold"
      >
        <ArrowLeft className="w-5 h-5 mr-2" /> Back to Dashboard
      </button>

      <div className="bg-surface-container-lowest rounded-xl shadow-[0_0_40px_rgba(50,41,79,0.06)] p-8">
        <h1 className="text-display-lg font-manrope font-bold mb-8">{project.title}</h1>

        <div className="space-y-6">
          <div>
            <label className="block text-sm font-bold text-on-surface mb-2 tracking-wide">VIDEO SCRIPT</label>
            <textarea
              className="w-full h-64 p-4 rounded-xl bg-surface-container-high text-on-surface focus:outline-none focus:ring-2 focus:ring-primary/40 focus:ring-offset-2 focus:ring-offset-surface-container-lowest resize-none"
              value={script}
              onChange={(e) => setScript(e.target.value)}
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-bold text-on-surface mb-2 tracking-wide">YOUTUBE TITLE</label>
              <input
                type="text"
                className="w-full p-4 rounded-xl bg-surface-container-high text-on-surface focus:outline-none focus:ring-2 focus:ring-primary/40"
                value={youtubeTitle}
                onChange={(e) => setYoutubeTitle(e.target.value)}
              />
            </div>
            <div>
              <label className="block text-sm font-bold text-on-surface mb-2 tracking-wide">NARRATOR VOICE</label>
              <select
                className="w-full p-4 rounded-xl bg-surface-container-high text-on-surface focus:outline-none focus:ring-2 focus:ring-primary/40"
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
              className="w-full h-32 p-4 rounded-xl bg-surface-container-high text-on-surface focus:outline-none focus:ring-2 focus:ring-primary/40 resize-none"
              value={youtubeDesc}
              onChange={(e) => setYoutubeDesc(e.target.value)}
            />
          </div>

          <div className="pt-8 flex justify-end space-x-4 border-t border-surface-container-highest">
            <button
              onClick={handleSave}
              disabled={saving}
              className="px-6 py-3 rounded-full font-bold text-primary border border-outline-variant/30 hover:bg-surface-container-low transition-colors inline-flex items-center"
            >
              <Save className="w-5 h-5 mr-2" /> Save Draft
            </button>
            <button
              onClick={handleApprove}
              className="px-8 py-3 rounded-full font-bold text-on-primary bg-gradient-to-r from-primary-dim to-primary shadow-sm hover:opacity-90 transition-opacity inline-flex items-center"
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
