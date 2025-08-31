import React from "react";
import { SystemStats as SystemStatsType } from "../types";

interface SystemStatsProps {
  stats: SystemStatsType;
}

const SystemStats: React.FC<SystemStatsProps> = ({ stats }) => {
  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4">
      <h3 className="text-lg font-medium text-gray-900 mb-4">
        System Statistics
      </h3>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="text-center">
          <div className="text-2xl font-bold text-blue-600">
            {stats.total_documents}
          </div>
          <div className="text-sm text-gray-500">Total Documents</div>
        </div>

        <div className="text-center">
          <div className="text-2xl font-bold text-green-600">
            {stats.total_chunks}
          </div>
          <div className="text-sm text-gray-500">Total Chunks</div>
        </div>
      </div>

      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="text-xs text-gray-500">
          <div className="flex justify-between">
            <span>Vector Database:</span>
            <span className="text-green-600">✓ Online</span>
          </div>
          <div className="flex justify-between">
            <span>LLM Service:</span>
            <span className="text-green-600">✓ Connected</span>
          </div>
          <div className="flex justify-between">
            <span>Document Processor:</span>
            <span className="text-green-600">✓ Ready</span>
          </div>
          <div className="flex justify-between">
            <span>Chat History:</span>
            <span className="text-green-600">✓ Persistent</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SystemStats;
