import React, { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import * as Switch from "@radix-ui/react-switch";
import { Sparkles, User, Copy, RefreshCw, MessageCircle } from "lucide-react";
import { Streamlit, withStreamlitConnection } from "streamlit-component-lib";

interface Props {
  args: {
    step: "input" | "questions" | "result";
    raw_prompt: string;
    questions?: string[];
    answers?: Record<string, string>;
    refined_prompt?: string;
    theme?: "light" | "dark";
    user?: {
      name: string;
      email: string;
      is_anonymous: boolean;
      remaining: number;
    };
  };
}

const App: React.FC<Props> = ({ args }) => {
  const [expanded, setExpanded] = useState(false);
  const [dark, setDark] = useState(args.theme === "dark");
  const [prompt, setPrompt] = useState(args.raw_prompt || "");
  const [answers, setAnswers] = useState<Record<string, string>>(args.answers || {});

  // Update local state if props change (e.g. re-run from Python)
  useEffect(() => {
    if (args.raw_prompt !== prompt) setPrompt(args.raw_prompt);
    if (args.answers) setAnswers(args.answers);
    if (args.theme) setDark(args.theme === "dark");
  }, [args.raw_prompt, args.answers, args.theme]);

  // Adjust iframe height dynamically
  useEffect(() => {
    Streamlit.setFrameHeight();
  });

  const sendAction = (action: string, data: any = {}) => {
    Streamlit.setComponentValue({ action, ...data });
  };

  const handleAnalyze = () => {
    sendAction("analyze", { prompt });
  };

  const handleRefine = () => {
    sendAction("refine", { answers });
  };

  const handleReset = () => {
    sendAction("reset");
    setPrompt("");
    setAnswers({});
  };

  const copyToClipboard = () => {
    if (args.refined_prompt) {
      navigator.clipboard.writeText(args.refined_prompt);
      // Could show toast here
    }
  };

  return (
    <div className={`${dark ? "dark" : ""}`}>
      <div className="flex min-h-screen bg-slate-50 dark:bg-slate-900 transition-colors duration-200 text-slate-900 dark:text-slate-100 font-sans">

        {/* Sidebar */}
        <motion.div
          onHoverStart={() => setExpanded(true)}
          onHoverEnd={() => setExpanded(false)}
          animate={{ width: expanded ? 256 : 64 }}
          transition={{ type: "spring", stiffness: 300, damping: 30 }}
          className="bg-white dark:bg-slate-800 border-r border-slate-200 dark:border-slate-700 p-4 flex flex-col fixed h-full z-10 shadow-sm"
        >
          <div className="flex items-center gap-3 mb-8">
            <div className="p-2 bg-orange-100 dark:bg-orange-900/30 rounded-lg text-orange-600 dark:text-orange-400">
              <Sparkles size={20} strokeWidth={2.5} />
            </div>
            {expanded && <span className="font-bold text-lg tracking-tight">Prompt Refiner</span>}
          </div>

          <div className="flex-1 space-y-2">
             {/* Main Nav Items */}
             <div className="flex items-center gap-3 p-2 rounded-lg bg-orange-50 dark:bg-orange-900/10 text-orange-700 dark:text-orange-400">
                <MessageCircle size={20} />
                {expanded && <span className="font-medium">Refine</span>}
             </div>
          </div>
          
          <div className="mt-auto pt-4 border-t border-slate-100 dark:border-slate-700">
             <div className="flex items-center gap-3 p-2 text-slate-500 dark:text-slate-400">
                <User size={20} />
                {expanded && (
                    <div className="text-sm">
                        <p className="font-medium text-slate-900 dark:text-slate-200">
                            {args.user?.is_anonymous ? "Guest" : "User"}
                        </p>
                        <p className="text-xs">
                            {args.user?.remaining} prompts left
                        </p>
                    </div>
                )}
             </div>
          </div>
        </motion.div>

        {/* Main Content */}
        <main className={`flex-1 transition-all duration-300 ${expanded ? "ml-64" : "ml-16"} p-8 max-w-5xl mx-auto w-full`}>
          
          <header className="flex justify-between items-center mb-10">
            <div>
                <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-slate-900 to-slate-700 dark:from-white dark:to-slate-400">
                    Refine Your Prompt
                </h1>
                <p className="text-slate-500 dark:text-slate-400 mt-1">
                    Transform basic ideas into powerful instructions.
                </p>
            </div>

            <div className="flex items-center gap-3">
                 <span className="text-sm font-medium text-slate-500 dark:text-slate-400">
                    {dark ? "Dark" : "Light"}
                 </span>
                <Switch.Root
                  checked={dark}
                  onCheckedChange={setDark}
                  className="w-11 h-6 bg-slate-200 dark:bg-slate-700 rounded-full relative shadow-inner focus:outline-none focus:ring-2 focus:ring-orange-500"
                >
                  <Switch.Thumb className="block w-5 h-5 bg-white rounded-full shadow-sm translate-x-0.5 transition-transform duration-200 will-change-transform data-[state=checked]:translate-x-5.5" />
                </Switch.Root>
            </div>
          </header>

          <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 p-6 md:p-8">
            
            <AnimatePresence mode="wait">
                {/* STEP 1: INPUT */}
                {args.step === "input" && (
                    <motion.div
                        key="step1"
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        transition={{ duration: 0.3 }}
                    >
                        <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                            Your Initial Prompt
                        </label>
                        <textarea
                            value={prompt}
                            onChange={(e) => setPrompt(e.target.value)}
                            placeholder="What do you want to achieve? Describe the task..."
                            className="w-full h-40 rounded-lg border border-slate-300 dark:border-slate-600 bg-slate-50 dark:bg-slate-900/50 p-4 text-slate-900 dark:text-slate-100 placeholder:text-slate-400 focus:ring-2 focus:ring-orange-500 focus:border-transparent outline-none transition-all resize-y"
                        />
                        <div className="mt-6 flex justify-end">
                            <motion.button
                                whileHover={{ scale: 1.02 }}
                                whileTap={{ scale: 0.98 }}
                                onClick={handleAnalyze}
                                className="bg-orange-600 hover:bg-orange-700 text-white font-medium rounded-lg px-6 py-2.5 shadow-sm shadow-orange-200 dark:shadow-none transition-colors flex items-center gap-2"
                            >
                                <Sparkles size={18} />
                                Analyze Prompt
                            </motion.button>
                        </div>
                    </motion.div>
                )}

                {/* STEP 2: QUESTIONS */}
                {args.step === "questions" && (
                     <motion.div
                        key="step2"
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        transition={{ duration: 0.3 }}
                    >
                        <div className="mb-6 bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg border border-blue-100 dark:border-blue-800 text-blue-800 dark:text-blue-200 text-sm">
                            <strong>Original:</strong> {prompt}
                        </div>
                        
                        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                             <MessageCircle size={20} className="text-orange-500" />
                             Clarifying Questions
                        </h3>

                        <div className="space-y-4">
                            {args.questions?.map((q, idx) => (
                                <div key={idx} className="space-y-1.5">
                                    <label className="text-sm font-medium text-slate-700 dark:text-slate-300">
                                        {idx + 1}. {q}
                                    </label>
                                    <input
                                        type="text"
                                        value={answers[q] || ""}
                                        onChange={(e) => setAnswers({...answers, [q]: e.target.value})}
                                        className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-900 px-4 py-2.5 focus:ring-2 focus:ring-orange-500 focus:border-transparent outline-none transition-all"
                                        placeholder="Your answer..."
                                    />
                                </div>
                            ))}
                        </div>

                        <div className="mt-8 flex justify-end gap-3">
                             <button
                                onClick={() => sendAction("back_to_input")}
                                className="px-4 py-2 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 font-medium transition-colors"
                             >
                                Back
                             </button>
                            <motion.button
                                whileHover={{ scale: 1.02 }}
                                whileTap={{ scale: 0.98 }}
                                onClick={handleRefine}
                                className="bg-orange-600 hover:bg-orange-700 text-white font-medium rounded-lg px-6 py-2.5 shadow-sm transition-colors flex items-center gap-2"
                            >
                                <Sparkles size={18} />
                                Generate Refined Prompt
                            </motion.button>
                        </div>
                    </motion.div>
                )}

                {/* STEP 3: RESULT */}
                {args.step === "result" && (
                    <motion.div
                        key="step3"
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        transition={{ duration: 0.3 }}
                    >
                        <div className="flex items-center justify-between mb-4">
                            <h3 className="text-lg font-semibold text-green-600 dark:text-green-400 flex items-center gap-2">
                                <Sparkles size={20} />
                                Refined Result
                            </h3>
                            <div className="flex gap-2">
                                <button
                                    onClick={copyToClipboard}
                                    className="p-2 text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200 transition-colors rounded-full hover:bg-slate-100 dark:hover:bg-slate-700"
                                    title="Copy to Clipboard"
                                >
                                    <Copy size={18} />
                                </button>
                            </div>
                        </div>

                        <div className="bg-slate-50 dark:bg-slate-900/50 border border-slate-200 dark:border-slate-700 p-6 rounded-lg font-mono text-sm leading-relaxed whitespace-pre-wrap text-slate-800 dark:text-slate-200 mb-8 max-h-[500px] overflow-y-auto">
                            {args.refined_prompt}
                        </div>

                        <div className="flex justify-end">
                            <motion.button
                                whileHover={{ scale: 1.02 }}
                                whileTap={{ scale: 0.98 }}
                                onClick={handleReset}
                                className="bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-600 text-slate-700 dark:text-slate-300 font-medium rounded-lg px-6 py-2.5 hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors flex items-center gap-2"
                            >
                                <RefreshCw size={18} />
                                Start Over
                            </motion.button>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>

          </div>
        </main>

      </div>
    </div>
  );
};

export default withStreamlitConnection(App);
