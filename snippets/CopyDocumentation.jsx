export const CopyDocumentation = ({ topic = "marko-documentation", label, chooseFamily = false }) => {
  const [state, setState] = useState("idle");
  const [message, setMessage] = useState("");
  const [selected, setSelected] = useState(topic);
  const [topics, setTopics] = useState([]);
  const base = "https://raw.githubusercontent.com/mathieuworoniecki/marko-developer-docs/main/downloads/";
  useEffect(() => {
    if (!chooseFamily) return;
    let active = true;
    fetch(base + "index.json").then(async (response) => {
      if (!response.ok) throw new Error("Index indisponible");
      const index = await response.json();
      if (active && index.format === "marko-documentation-index/v1") setTopics(index.topics);
    }).catch(() => {
      if (active) setMessage("La liste des périmètres est indisponible. La copie complète reste accessible.");
    });
    return () => { active = false; };
  }, [chooseFamily]);
  const id = chooseFamily ? selected : topic;
  const downloadUrl = base + encodeURIComponent(id) + ".json";
  const copy = async () => {
    setState("loading");
    setMessage("");
    try {
      const document = fetch(downloadUrl).then(async (response) => {
        if (!response.ok) throw new Error("Documentation indisponible");
        const payload = await response.json();
        const text = payload.markdown;
        if (payload.format !== "marko-documentation/v1" || typeof text !== "string" || !text.startsWith("# MARKO — ")) {
          throw new Error("Format de documentation inattendu");
        }
        return text;
      });
      if (navigator.clipboard.write && typeof ClipboardItem !== "undefined") {
        await navigator.clipboard.write([
          new ClipboardItem({ "text/plain": document.then((text) => new Blob([text], { type: "text/plain" })) }),
        ]);
      } else {
        await navigator.clipboard.writeText(await document);
      }
      setState("copied");
      setMessage("Documentation copiée. Vous pouvez la coller dans votre assistant.");
    } catch {
      setState("error");
      setMessage("La copie n'a pas abouti. Utilisez le lien de téléchargement ci-dessous.");
    }
  };
  return (
    <div className="not-prose my-4">
      {chooseFamily && (
        <label className="mb-3 block text-sm">
          <span className="mb-1 block">Documentation à copier</span>
          <select
            aria-label="Documentation à copier"
            value={selected}
            disabled={state === "loading"}
            onChange={(event) => { setSelected(event.target.value); setState("idle"); setMessage(""); }}
            className="w-full rounded-lg border px-3 py-2"
            style={{ color: "inherit", backgroundColor: "transparent", borderColor: "#087E8B" }}
          >
            {!topics.length && <option value="marko-documentation">Toute la documentation</option>}
            {topics.map((item) => <option key={item.id} value={item.id}>{item.kind === "tutorial" ? "Tutoriel : " : item.kind === "family" ? "API : " : ""}{item.title}</option>)}
          </select>
        </label>
      )}
      <button
        type="button"
        onClick={copy}
        disabled={state === "loading"}
        className="rounded-lg border px-4 py-2 text-sm font-semibold disabled:opacity-60 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2"
        style={{ backgroundColor: "#76E7F4", color: "#092E33", borderColor: "#087E8B" }}
      >
        {state === "loading" ? "Copie en cours…" : state === "copied" ? "Documentation copiée ✓" : label || (chooseFamily ? "Copier la sélection pour une IA" : "Copier toute la documentation pour une IA")}
      </button>
      <p className="mt-2 text-sm" role="status" aria-live="polite">{message}</p>
      <a className="text-sm underline" href={downloadUrl}>{chooseFamily || topic !== "marko-documentation" ? "Télécharger cette documentation" : "Télécharger la documentation complète"}</a>
    </div>
  );
};
