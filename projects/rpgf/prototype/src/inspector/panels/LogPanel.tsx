import { useEffect, useRef } from "react";
import type { AppState } from "../store";

interface Props { state: AppState; }

export function LogPanel({ state }: Props) {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (ref.current) ref.current.scrollTop = ref.current.scrollHeight;
  }, [state.log]);

  return (
    <div className="panel">
      <h2>Event log</h2>
      <div className="log" ref={ref}>
        {state.log.map((entry, i) => (
          <div key={i} className="log-entry">
            <span className="log-tick">{entry.tick}</span>
            <span className={`log-cat ${entry.category}`}>{entry.category}</span>
            <span>{entry.message}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
