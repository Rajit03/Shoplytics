import React from 'react';
import { AlertCircle, RefreshCw } from 'lucide-react';

export const ErrorMessage = ({
  title = 'Unable to connect to Shoplytics API',
  message = 'Please ensure FastAPI is running at http://127.0.0.1:8000',
  onRetry = null,
}) => {
  return (
    <div className="rounded-xl border border-rose-500/30 bg-rose-950/20 p-6 backdrop-blur-sm text-slate-200 shadow-xl my-4">
      <div className="flex items-start space-x-4">
        <div className="p-2 rounded-lg bg-rose-500/10 text-rose-400">
          <AlertCircle className="w-6 h-6" />
        </div>
        <div className="flex-1">
          <h3 className="text-base font-semibold text-rose-300">{title}</h3>
          <p className="mt-1 text-sm text-slate-300">{message}</p>
          <div className="mt-3 flex items-center space-x-3">
            <span className="text-xs text-slate-400 font-mono bg-slate-900/60 px-2.5 py-1 rounded border border-slate-800">
              API Base: http://127.0.0.1:8000
            </span>
            {onRetry && (
              <button
                onClick={onRetry}
                className="inline-flex items-center space-x-1.5 px-3 py-1 text-xs font-medium text-white bg-rose-600 hover:bg-rose-500 rounded-lg transition-colors shadow-sm"
              >
                <RefreshCw className="w-3.5 h-3.5" />
                <span>Retry Connection</span>
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ErrorMessage;
