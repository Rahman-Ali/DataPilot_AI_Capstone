export default function PageIntro({ eyebrow, title, description, status = 'Ready' }) {
  return (
    <header className="max-w-4xl">
      <div className="flex flex-wrap items-center gap-3">
        <p className="text-xs font-bold tracking-[0.2em] text-mint-400 uppercase">{eyebrow}</p>
        <span className="h-px w-8 bg-line" />
        <span className="inline-flex items-center gap-2 text-xs font-medium text-muted">
          <span className="size-1.5 rounded-full bg-mint-400 shadow-[0_0_8px_#45e6c1]" /> {status}
        </span>
      </div>
      <h1 className="text-gradient mt-5 text-4xl leading-[1.05] font-bold tracking-[-0.045em] sm:text-6xl">{title}</h1>
      <p className="mt-5 max-w-2xl text-base leading-7 text-muted sm:text-lg">{description}</p>
    </header>
  )
}
