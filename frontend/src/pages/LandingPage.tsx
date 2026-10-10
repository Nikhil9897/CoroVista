import React, { useState, useRef } from "react"
import { Link } from "react-router-dom"
import {
  Activity,
  ArrowRight,
  Sparkles,
  Layers,
  Info,
  Sliders,
  Cpu,
  Binary,
  ChevronLeft,
  ChevronRight,
  FileText,
  Heart,
} from "lucide-react"
import type { HealthResponse } from "@/types/patient"
import { LandingHero } from "@/components/landing/hero/LandingHero"
import { ScrollReveal } from "@/components/landing/ScrollReveal"
import CardSwap, { Card, type CardSwapRef } from "@/components/landing/CardSwap"
import { CircuitBoard, type CircuitNode, type CircuitConnection } from "@/components/landing/CircuitBoard"

interface LandingPageProps {
  health: HealthResponse | null
}

export const LandingPage: React.FC<LandingPageProps> = ({ health }) => {
  const cardSwapRef = useRef<CardSwapRef>(null)
  const [activeCardIndex, setActiveCardIndex] = useState<number>(0)

  const capabilities = [
    {
      index: "01",
      category: "ARCHITECTURE",
      title: "Multi-Target Prediction Architecture",
      subtitle: "Four locked machine learning pipelines evaluated simultaneously.",
      description:
        "Decoupled XGBoost and Logistic Regression pipelines simultaneously predicting overall CAD alongside vessel-specific stenosis across LAD, LCX, and RCA.",
      badge: "4 Target Pipelines",
      icon: <Binary className="w-5 h-5 text-emerald-600" />,
      accent: "text-emerald-700 bg-emerald-50 border-emerald-200",
      footer: "Locked Benchmarks • Zero Target Leakage",
      metrics: [
        { label: "Cath (CAD)", value: "76.6%", tag: "Balanced F1" },
        { label: "LAD Stenosis", value: "53.2%", tag: "Platt Scaled" },
        { label: "RCA Stenosis", value: "40.1%", tag: "θ = 0.38" },
      ],
    },
    {
      index: "02",
      category: "3D SHADERS",
      title: "Continuous 3D Coronary Risk Shaders",
      subtitle: "Smooth vertex color gradients registered to BodyParts3D anatomical geometry.",
      description:
        "Monotonic probability gradients mapped directly to anatomical coronary geometry, replacing discrete binary boundaries with continuous biological risk transitions.",
      badge: "BodyParts3D Registered",
      icon: <Sparkles className="w-5 h-5 text-cyan-600" />,
      accent: "text-cyan-700 bg-cyan-50 border-cyan-200",
      footer: "Smooth Vertex Color Interpolation",
      metrics: [
        { label: "Anatomy Source", value: "BodyParts3D", tag: "Physiological" },
        { label: "Color Spectrum", value: "Continuous", tag: "Teal → Amber → Coral" },
        { label: "Precision Frame", value: "Millimeter", tag: "DICOM Space" },
      ],
    },
    {
      index: "03",
      category: "TREESHAP",
      title: "Local TreeSHAP Feature Attributions",
      subtitle: "Exact mathematical additivity in model score (log-odds) margin space.",
      description:
        "Mathematically additive explanations computed in uncalibrated log-odds space, isolating exactly how individual ECG and biomarker values steer model confidence.",
      badge: "Exact Lundberg Additivity",
      icon: <Layers className="w-5 h-5 text-amber-600" />,
      accent: "text-amber-700 bg-amber-50 border-amber-200",
      footer: "Game-Theoretic Shapley Efficiency",
      metrics: [
        { label: "Top Risk Driver", value: "T-Inversion", tag: "+0.46 log-odds" },
        { label: "Top Protective", value: "Typical Pain", tag: "-0.77 log-odds" },
        { label: "Additive Axiom", value: "φ₀ + Σφᵢ = f(x)", tag: "Exact Match" },
      ],
    },
    {
      index: "04",
      category: "CALIBRATION",
      title: "Decoupled Platt Sigmoid Calibration",
      subtitle: "Transparent separation between raw margin scores and clinical risk probabilities.",
      description:
        "Separates uncalibrated margin score explanations from downstream posterior probabilities, preserving TreeSHAP additivity while maximizing probabilistic calibration.",
      badge: "Brier-Optimized Calibration",
      icon: <Activity className="w-5 h-5 text-indigo-600" />,
      accent: "text-indigo-700 bg-indigo-50 border-indigo-200",
      footer: "Strict Separation of Scale & Attribution",
      metrics: [
        { label: "Cath Calibration", value: "Platt Sigmoid", tag: "Brier: 0.124" },
        { label: "LAD Calibration", value: "Platt Sigmoid", tag: "Brier: 0.165" },
        { label: "RCA Boundary", value: "θ = 0.38", tag: "89% Sensitivity" },
      ],
    },
    {
      index: "05",
      category: "SIMULATOR",
      title: "Interactive Sensitivity Simulator",
      subtitle: "Tune 54 clinical inputs and observe instant multi-target delta trajectories.",
      description:
        "Dynamic 'what-if' exploration allowing clinicians to manipulate lab biomarkers, hemodynamics, and ECG findings to observe immediate cross-vessel risk trajectories.",
      badge: "54 Clinical Features",
      icon: <Sliders className="w-5 h-5 text-rose-600" />,
      accent: "text-rose-700 bg-rose-50 border-rose-200",
      footer: "Real-Time Cross-Vessel Sensitivity Deltas",
      metrics: [
        { label: "Exam & Vitals", value: "16 Features", tag: "BP, BMI, Age..." },
        { label: "ECG & Cardiac", value: "11 Features", tag: "ST, T-Wave, LVH..." },
        { label: "Echo & Labs", value: "27 Features", tag: "Lipids, EF, Enzymes..." },
      ],
    },
  ]

  const workflowNodes: CircuitNode[] = [
    {
      id: "ingestion",
      x: 80,
      y: 150,
      label: "Data Ingestion",
      sublabel: "54 Features",
      icon: <FileText className="w-5 h-5 text-teal-400" />,
      description: "Normalized 54 demographic, physical exam, ECG, laboratory, and echocardiographic parameters validated via Pydantic schemas.",
      badge: "Zero-Leakage Ingestion",
    },
    {
      id: "inference",
      x: 270,
      y: 80,
      label: "ML Inference",
      sublabel: "4 Ensembles",
      icon: <Cpu className="w-5 h-5 text-emerald-400" />,
      description: "Parallel multi-target evaluation across Cath, LAD, LCX, and RCA with target-specific thresholds (RCA θ = 0.38).",
      badge: "Target-Locked XGBoost",
    },
    {
      id: "explainability",
      x: 270,
      y: 220,
      label: "TreeSHAP",
      sublabel: "Log-Odds Space",
      icon: <Layers className="w-5 h-5 text-amber-400" />,
      description: "Exact Lundberg feature attributions in uncalibrated log-odds space isolating precise risk-driving factors.",
      badge: "Exact Additive Axiom",
    },
    {
      id: "twin",
      x: 460,
      y: 150,
      label: "Clinical Twin",
      sublabel: "3D & Platt Scaled",
      icon: <Heart className="w-5 h-5 text-rose-400" />,
      description: "Decoupled Platt sigmoid calibrated posterior probabilities projected onto BodyParts3D continuous vertex risk shaders.",
      badge: "Calibrated 3D Output",
    },
  ]

  const workflowConnections: CircuitConnection[] = [
    { from: "ingestion", to: "inference", animated: true },
    { from: "ingestion", to: "explainability", animated: true },
    { from: "inference", to: "twin", animated: true },
    { from: "explainability", to: "twin", animated: true },
  ]

  return (
    <div className="min-h-screen bg-[#02050f] text-slate-100 selection:bg-indigo-500/30 selection:text-white relative overflow-x-hidden">
      {/* ── Section 1: Refined Visual Reference Hero Section (Deep Teal & Mint) ── */}
      <LandingHero health={health} />

      {/* ── Seamless Color Blend: Hero (#011719) → Capabilities (#cecbcb) ── */}
      <div
        className="w-full h-16 sm:h-20 bg-gradient-to-b from-[#011719] to-[#cecbcb] pointer-events-none -mb-1"
        aria-hidden="true"
      />

      {/* ── Section 2: Multimodal AI Architecture (Exact #cecbcb Swatch, No Hard Borders) ── */}
      <section
        id="capabilities"
        className="relative bg-[#cecbcb] text-[#0f172a] py-20 sm:py-24 px-4 sm:px-8 overflow-hidden"
      >
        <div className="max-w-7xl mx-auto relative z-10">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 lg:gap-12 xl:gap-16 items-center">
            {/* Left Column: Bold One-Liner Heading, Narrative, Live Telemetry & Card Swap Controls */}
            <div className="lg:col-span-5 space-y-6 max-w-lg">
              <ScrollReveal delay={0}>
                <div className="space-y-4">
                  {/* Bold One-Liner Heading */}
                  <h2 className="text-3xl sm:text-4xl lg:text-[40px] xl:text-5xl font-bold tracking-tight text-[#0f172a] leading-[1.14]">
                    Five Synchronized Multimodal AI Pipelines Transforming Cardiovascular Risk Stratification
                  </h2>

                  <p className="text-sm sm:text-base text-[#475569] leading-relaxed font-sans max-w-md">
                    Translating 54 complex multimodal patient parameters into calibrated, spatially mapped arterial decision support across four independent coronary targets.
                  </p>

                  {/* Spatial AI Live Telemetry Chip */}
                  <div className="inline-flex items-center gap-3 px-3 py-1.5 rounded-xl bg-white/70 border border-neutral-300 text-[11px] font-mono text-neutral-700 shadow-xs">
                    <Cpu className="w-3.5 h-3.5 text-primary shrink-0" />
                    <span>4 Target Ensembles • 54 Continuous Features • TreeSHAP Log-Odds Additivity</span>
                  </div>
                </div>
              </ScrollReveal>

              {/* Card Deck Controls & Live Progress */}
              <ScrollReveal delay={100}>
                <div className="pt-4 border-t border-neutral-300/80 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                  <div className="flex items-center gap-3">
                    <div className="flex items-center gap-1.5">
                      <button
                        type="button"
                        onClick={() => cardSwapRef.current?.prev()}
                        className="w-9 h-9 rounded-full bg-white border border-neutral-300 flex items-center justify-center text-neutral-700 hover:bg-neutral-50 hover:border-neutral-400 transition-colors shadow-xs cursor-pointer active:scale-95"
                        aria-label="Previous card"
                      >
                        <ChevronLeft className="w-4 h-4" />
                      </button>
                      <button
                        type="button"
                        onClick={() => cardSwapRef.current?.next()}
                        className="w-9 h-9 rounded-full bg-white border border-neutral-300 flex items-center justify-center text-neutral-700 hover:bg-neutral-50 hover:border-neutral-400 transition-colors shadow-xs cursor-pointer active:scale-95"
                        aria-label="Next card"
                      >
                        <ChevronRight className="w-4 h-4" />
                      </button>
                    </div>

                    <div className="text-xs font-mono text-neutral-600">
                      <span className="font-semibold text-[#0f172a]">{String(activeCardIndex + 1).padStart(2, "0")}</span>
                      <span className="text-neutral-400"> / 05</span>
                      <span className="hidden sm:inline text-neutral-400"> • Fast-cycling</span>
                    </div>
                  </div>

                  <Link
                    to="/dashboard"
                    className="inline-flex items-center gap-1.5 text-xs font-bold text-primary hover:text-primary/80 transition-colors font-mono uppercase tracking-wider"
                  >
                    <span>Launch Workspace</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </Link>
                </div>
              </ScrollReveal>
            </div>

            {/* Right Column: Card Swap Animation Component anchored cleanly to the right */}
            <div className="lg:col-span-7 w-full flex items-center justify-center lg:justify-end">
              <ScrollReveal delay={150} className="w-full flex justify-center lg:justify-end">
                <div className="w-full relative flex items-center justify-center lg:justify-end min-h-[460px] sm:min-h-[500px]">
                  <CardSwap
                    ref={cardSwapRef}
                    width={470}
                    height={350}
                    cardDistance={32}
                    verticalDistance={44}
                    depth={65}
                    skewAmount={3.5}
                    visibleCards={4}
                    delay={2600}
                    autoplay={true}
                    pauseOnHover={true}
                    draggable={true}
                    speed={2.2}
                    bounce={0.25}
                    theme="light"
                    cardRadius={22}
                    className="lg:ml-auto"
                    onChange={(idx) => setActiveCardIndex(idx)}
                  >
                    {capabilities.map((cap) => (
                      <Card
                        key={cap.index}
                        className="p-7 sm:p-8 flex flex-col justify-between bg-white text-[#0f172a] shadow-2xl border border-neutral-300/80 rounded-2xl"
                      >
                        <div className="space-y-3.5">
                          {/* Card Top Category & Status Badge */}
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2.5">
                              <div className={`p-2 rounded-xl border ${cap.accent}`}>
                                {cap.icon}
                              </div>
                              <span className="font-mono text-xs font-bold text-[#0f172a] tracking-wider">
                                {cap.index} // {cap.category}
                              </span>
                            </div>
                            <span className="text-[11px] font-mono px-3 py-1 rounded-full bg-neutral-100 text-neutral-800 border border-neutral-200 font-semibold shrink-0">
                              {cap.badge}
                            </span>
                          </div>

                          {/* Card Title & Subtitle */}
                          <div>
                            <h3 className="text-xl sm:text-2xl font-bold tracking-tight text-[#0f172a]">
                              {cap.title}
                            </h3>
                            <p className="text-xs text-neutral-500 font-mono mt-1">
                              {cap.subtitle}
                            </p>
                          </div>

                          {/* Crisp, professional core insight */}
                          <p className="text-xs sm:text-[13px] text-[#475569] leading-relaxed">
                            {cap.description}
                          </p>

                          {/* 3 High-Impact Key Metrics */}
                          <div className="grid grid-cols-3 gap-2.5 pt-1">
                            {cap.metrics.map((m, idx) => (
                              <div
                                key={idx}
                                className="bg-neutral-50/95 border border-neutral-200/90 rounded-xl p-3 text-left shadow-2xs"
                              >
                                <span className="text-[10px] font-mono text-neutral-500 uppercase block truncate">
                                  {m.label}
                                </span>
                                <span className="text-base sm:text-lg font-bold text-[#0f172a] block mt-0.5 font-mono">
                                  {m.value}
                                </span>
                                <span className="text-[10px] text-primary font-medium block mt-0.5 truncate">
                                  {m.tag}
                                </span>
                              </div>
                            ))}
                          </div>
                        </div>

                        {/* Card Bottom Micro-Indicator */}
                        <div className="pt-3.5 border-t border-neutral-200/80 flex items-center justify-between text-[11px] text-neutral-500 font-mono">
                          <span>{cap.footer}</span>
                          <span className="text-primary font-semibold flex items-center gap-1">
                            Drag or click to swap &rarr;
                          </span>
                        </div>
                      </Card>
                    ))}
                  </CardSwap>
                </div>
              </ScrollReveal>
            </div>
          </div>
        </div>
      </section>

      {/* ── Seamless Color Blend: Capabilities (#cecbcb) → Workflow (#040a16) ── */}
      <div
        className="w-full h-28 sm:h-40 bg-gradient-to-b from-[#cecbcb] via-[#606775] to-[#040a16] pointer-events-none -mb-1"
        aria-hidden="true"
      />

      {/* ── Section 3: Clinical Decision Workflow (Circuit Board Animation Flow Diagram) ── */}
      <section
        id="workflow"
        className="relative bg-[#040a16] text-slate-100 py-24 sm:py-28 px-4 sm:px-8 overflow-hidden"
      >
        <div className="max-w-5xl mx-auto space-y-12 relative z-10">
          <ScrollReveal delay={0}>
            <div className="text-center max-w-2xl mx-auto space-y-4">
              <h2 className="text-3xl sm:text-4xl lg:text-5xl font-normal tracking-tight text-white font-serif">
                How CoroVista Operates <br />
                <span className="italic text-teal-300 font-normal">from Features to Insights</span>
              </h2>
              <p className="text-sm text-slate-300/80 leading-relaxed font-sans">
                A 4-stage pipeline translating multimodal clinical inputs into calibrated predictions and interactive 3D risk models.
              </p>
            </div>
          </ScrollReveal>

          {/* Circuit Board 4-Block Animated Flow Diagram */}
          <ScrollReveal delay={100}>
            <CircuitBoard
              nodes={workflowNodes}
              connections={workflowConnections}
              width={540}
              height={300}
              className="w-full max-w-3xl mx-auto"
            />
          </ScrollReveal>
        </div>
      </section>

      {/* ── Seamless Color Blend: Workflow (#040a16) → CTA (#050611) ── */}
      <div
        className="w-full h-20 sm:h-28 bg-gradient-to-b from-[#040a16] to-[#050611] pointer-events-none -mb-1"
        aria-hidden="true"
      />

      {/* ── Section 4: Responsible Use & Final CTA (Cosmic Obsidian & Dual Aurora Palette) ── */}
      <section id="cta" className="relative bg-[#050611] py-24 sm:py-28 px-4 sm:px-8 overflow-hidden">
        {/* Dual Aurora Glows */}
        <div
          aria-hidden="true"
          className="absolute -top-32 left-1/3 w-[34rem] h-[34rem] rounded-full bg-rose-500/10 blur-[130px] pointer-events-none"
        />
        <div
          aria-hidden="true"
          className="absolute bottom-10 right-1/4 w-[28rem] h-[28rem] rounded-full bg-indigo-500/10 blur-[120px] pointer-events-none"
        />

        <div className="max-w-5xl mx-auto space-y-16 relative z-10">
          {/* Regulatory Notice Card */}
          <ScrollReveal delay={0}>
            <div className="bg-[#141208]/80 border border-amber-500/30 rounded-2xl p-6 sm:p-8 space-y-3.5 text-amber-200/90 backdrop-blur-md shadow-xl">
              <div className="flex items-center gap-2.5 text-amber-400 font-semibold text-sm">
                <Info className="w-4 h-4 shrink-0" />
                <span>Clinical &amp; Regulatory Decision-Support Notice</span>
              </div>
              <p className="text-xs text-amber-200/80 leading-relaxed font-sans">
                CoroVista is an educational and clinical decision-support research prototype based on the Z-Alizadeh Sani cohort ($N=303$). Model predictions reflect observational statistical likelihood of luminal stenosis (≥ 50%) and do not establish biological causality. Predicted vessel probabilities are not physical lesion coordinates or surgical navigation markers. Model outputs do not replace formal coronary angiography or physician diagnosis.
              </p>
            </div>
          </ScrollReveal>

          {/* Final Launchpad CTA */}
          <div className="text-center space-y-8">
            <ScrollReveal delay={100}>
              <div className="max-w-2xl mx-auto space-y-4">
                <h2 className="text-3xl sm:text-4xl lg:text-5xl font-normal tracking-tight text-white font-serif">
                  Accelerate Clinical Cardiovascular Assessment
                </h2>
                <p className="text-sm text-slate-300/80 leading-relaxed max-w-xl mx-auto">
                  Launch the clinical risk workspace to evaluate multi-target stenosis predictions, interact with 3D coronary anatomy, and explore SHAP waterfalls.
                </p>
              </div>
            </ScrollReveal>

            <ScrollReveal delay={200}>
              <div className="flex flex-wrap items-center justify-center gap-4 pt-2">
                <Link
                  to="/dashboard"
                  className="inline-flex items-center gap-2.5 px-8 py-4 rounded-full text-sm font-semibold bg-gradient-to-r from-[#ff7e81] to-[#f43f5e] hover:from-[#ff8e91] hover:to-[#fb7185] text-white shadow-xl shadow-rose-500/25 transition-all duration-300 hover:scale-105 active:scale-95"
                >
                  <span>Open Clinical Dashboard</span>
                  <ArrowRight className="w-4 h-4" />
                </Link>

                <Link
                  to="/simulator"
                  className="inline-flex items-center gap-2.5 px-8 py-4 rounded-full text-sm font-semibold bg-white/5 hover:bg-white/10 text-white border border-white/20 hover:border-white/40 backdrop-blur-md transition-all duration-300 hover:scale-105 active:scale-95"
                >
                  <Sliders className="w-4 h-4 text-indigo-400" />
                  <span>Launch Patient Simulator</span>
                </Link>
              </div>
            </ScrollReveal>
          </div>
        </div>
      </section>

      {/* ── Seamless Color Blend: CTA (#050611) → Footer (#020308) ── */}
      <div
        className="w-full h-16 sm:h-20 bg-gradient-to-b from-[#050611] to-[#020308] pointer-events-none -mb-1"
        aria-hidden="true"
      />

      {/* ── Product Footer ── */}
      <footer className="bg-[#020308] py-14 px-4 sm:px-8 text-xs text-slate-400">
        <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-8 mb-10">
          <ScrollReveal delay={50}>
            <div className="space-y-3">
              <div className="flex items-center gap-3">
                <img
                  src="/corovista-logo-dark.png"
                  alt="CoroVista Logo"
                  className="h-8 w-auto object-contain drop-shadow-[0_0_12px_rgba(56,189,248,0.25)]"
                />
                <span className="font-semibold text-white text-sm sr-only">CoroVista</span>
              </div>
              <p className="text-[11px] leading-relaxed text-slate-400/80">
                Cardiovascular Risk Visualization &amp; Multi-Target Stenosis Prediction Platform.
              </p>
            </div>
          </ScrollReveal>

          <ScrollReveal delay={100}>
            <div className="space-y-2">
              <span className="font-semibold text-white block mb-2 font-mono text-[11px] uppercase tracking-wider">Navigation</span>
              <div><Link to="/dashboard" className="text-slate-400 hover:text-white transition-colors">Analysis Workspace</Link></div>
              <div><Link to="/simulator" className="text-slate-400 hover:text-white transition-colors">Interactive Simulator</Link></div>
              <div><Link to="/about" className="text-slate-400 hover:text-white transition-colors">Methodology Documentation</Link></div>
            </div>
          </ScrollReveal>

          <ScrollReveal delay={150}>
            <div className="space-y-2">
              <span className="font-semibold text-white block mb-2 font-mono text-[11px] uppercase tracking-wider">Scientific Baseline</span>
              <div>Z-Alizadeh Sani Cohort ($N=303$)</div>
              <div>25-Run Stratified CV Benchmark</div>
              <div>TreeSHAP Margin Efficiency</div>
              <div>Platt Sigmoid Calibration</div>
            </div>
          </ScrollReveal>

          <ScrollReveal delay={200}>
            <div className="space-y-2">
              <span className="font-semibold text-white block mb-2 font-mono text-[11px] uppercase tracking-wider">Attribution &amp; License</span>
              <div>Code: MIT License</div>
              <div>Anatomy: BodyParts3D (CC BY-SA 2.1 Japan)</div>
              <div>Database Center for Life Science (DBCLS)</div>
            </div>
          </ScrollReveal>
        </div>

        <ScrollReveal delay={250}>
          <div className="max-w-7xl mx-auto pt-6 border-t border-white/10 flex flex-col sm:flex-row items-center justify-between gap-4 text-[11px] text-slate-500">
            <div>&copy; 2026 CoroVista Research Systems. All rights reserved.</div>
            <div>Clinical Decision Support &amp; Educational Research Prototype</div>
          </div>
        </ScrollReveal>
      </footer>
    </div>
  )
}
