import React from 'react';
import { Loader2 } from 'lucide-react';

export const Loading = ({ message = 'Loading analytics data...', fullScreen = false }) => {
  const content = (
    <div className="flex flex-col items-center justify-center p-8 text-center space-y-4">
      <div className="relative">
        <div className="w-12 h-12 rounded-full border-2 border-indigo-500/20 animate-ping absolute inset-0" />
        <Loader2 className="w-12 h-12 text-indigo-400 animate-spin" />
      </div>
      <p className="text-sm font-medium text-slate-400 animate-pulse">{message}</p>
    </div>
  );

  if (fullScreen) {
    return (
      <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center">
        {content}
      </div>
    );
  }

  return content;
};

export default Loading;
