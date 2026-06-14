'use client';

import { motion } from 'framer-motion';
import { useUserTrailStore } from '@/lib/store/user-trail';

export default function BreadcrumbTrail() {
  const getHistory = useUserTrailStore((s) => s.getHistory);
  const history = getHistory();

  if (history.length === 0) return null;

  const steps = history.slice(-5);

  return (
    <motion.nav
      initial={{ opacity: 0, y: -8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="flex items-center gap-0"
    >
      {steps.map((step, i) => {
        const isLast = i === steps.length - 1;
        return (
          <div key={step.path} className="flex items-center">
            {i > 0 && (
              <svg width="32" height="12" className="mx-1 flex-shrink-0">
                <line
                  x1="0"
                  y1="6"
                  x2="32"
                  y2="6"
                  stroke="#374151"
                  strokeWidth="2"
                  strokeDasharray="4 3"
                />
              </svg>
            )}
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: i * 0.1 }}
              className="flex items-center gap-1.5"
            >
              <span className="relative flex h-2.5 w-2.5 flex-shrink-0">
                {isLast ? (
                  <>
                    <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-[#3b82f6] opacity-60" />
                    <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-[#3b82f6]" />
                  </>
                ) : (
                  <>
                    <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-[#10b981] opacity-50" />
                    <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-[#10b981]" />
                  </>
                )}
              </span>
              <span
                className={`text-xs whitespace-nowrap ${
                  isLast ? 'text-white font-semibold' : 'text-gray-400'
                }`}
              >
                {step.label}
              </span>
            </motion.div>
          </div>
        );
      })}
    </motion.nav>
  );
}
