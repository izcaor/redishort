import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { PlayCircle, Clock, CheckCircle, AlertCircle, FileText, Radio } from 'lucide-react';

function Dashboard() {
  const [projects, setProjects] = useState([]);
  const [sources, setSources] = useState([]);

  useEffect(() => {
    fetchProjects();
    fetchSources();
  }, []);

  const fetchProjects = async () => {
    try {
      const res = await axios.get('/api/projects');
      setProjects(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const fetchSources = async () => {
    try {
      const res = await axios.get('/api/sources');
      setSources(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'new': return <FileText className="w-5 h-5 text-on-surface-variant" />;
      case 'drafting': return <Clock className="w-5 h-5 text-on-surface-variant" />;
      case 'pending_approval': return <AlertCircle className="w-5 h-5 text-primary" />;
      case 'processing': return <Clock className="w-5 h-5 text-secondary-container" />;
      case 'completed': return <CheckCircle className="w-5 h-5 text-secondary-container" />;
      case 'failed': return <AlertCircle className="w-5 h-5 text-tertiary" />;
      default: return <FileText className="w-5 h-5 text-on-surface-variant" />;
    }
  };

  return (
    <div className="max-w-7xl mx-auto space-y-12">
      <section className="rounded-3xl border border-outline-variant/40 bg-surface-container-low/60 p-8 shadow-glow">
        <div className="flex flex-wrap items-center justify-between gap-4 mb-8">
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-secondary-container font-semibold mb-2">Brand-aligned dashboard</p>
            <h2 className="text-4xl font-manrope font-extrabold tracking-tight">Video Drafts</h2>
          </div>
          <span className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-surface-container text-on-surface-variant text-sm font-semibold">
            <Radio className="w-4 h-4 text-primary" /> {projects.length} total
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {projects.map((project) => (
            <div key={project.id} className="rounded-2xl p-6 flex flex-col justify-between border border-outline-variant/40 bg-gradient-to-b from-surface-container-lowest to-surface-container shadow-brand">
              <div>
                <div className="flex justify-between items-start mb-4">
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-surface-container text-on-surface">
                    {project.status.toUpperCase().replace('_', ' ')}
                  </span>
                  {getStatusIcon(project.status)}
                </div>
                <h3 className="text-xl font-bold font-inter mb-2 text-on-surface line-clamp-2">{project.title}</h3>
                <p className="text-sm text-on-surface-variant mb-6">Source: {project.source_type}</p>
              </div>
              <div className="mt-auto">
                {project.status === 'pending_approval' ? (
                  <Link
                    to={`/review/${project.id}`}
                    className="w-full inline-flex justify-center items-center px-4 py-3 rounded-full font-bold text-on-primary bg-gradient-to-r from-primary-dim to-primary shadow-sm hover:brightness-110 transition"
                  >
                    Review & Edit <PlayCircle className="ml-2 w-4 h-4" />
                  </Link>
                ) : (
                  <button disabled className="w-full inline-flex justify-center items-center px-4 py-3 rounded-full font-bold text-on-surface-variant bg-surface-container-high cursor-not-allowed">
                    {project.status === 'completed' ? 'Published' : 'Processing...'}
                  </button>
                )}
              </div>
            </div>
          ))}
          {projects.length === 0 && (
            <div className="col-span-full py-12 text-center text-on-surface-variant rounded-2xl border border-dashed border-outline-variant bg-surface-container-low">
              No drafts available.
            </div>
          )}
        </div>
      </section>

      <section>
        <h2 className="text-3xl font-manrope font-extrabold tracking-tight mb-5">Content Sources</h2>
        <div className="rounded-2xl border border-outline-variant/40 bg-surface-container-lowest/90 p-6 shadow-glow">
          {sources.length > 0 ? (
            <div className="divide-y divide-outline-variant/30">
              {sources.map(source => (
                <div key={source.id} className="py-4 flex items-center justify-between hover:bg-surface-container-high/30 transition-colors px-4 -mx-4 rounded-lg">
                  <div>
                    <h4 className="font-bold font-inter">{source.name || source.source_url}</h4>
                    <span className="text-xs text-on-surface-variant uppercase tracking-wider">{source.source_type}</span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-on-surface-variant">
              No content sources configured.
            </div>
          )}
        </div>
      </section>
    </div>
  );
}

export default Dashboard;
