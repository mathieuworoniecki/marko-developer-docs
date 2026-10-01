export const CopyDocumentation = () => {
  const [state, setState] = useState("idle");
  const [message, setMessage] = useState("");
  const copy = async () => {
    setState("loading");
    setMessage("");
    try {
      const document = fetch("https://raw.githubusercontent.com/mathieuworoniecki/marko-developer-docs/main/downloads/marko-documentation.json").then(async (response) => {
        if (!response.ok) throw new Error("Documentation indisponible");
        const payload = await response.json();
        const text = payload.markdown;
        if (typeof text !== "string" || !text.startsWith("# MARKO — Documentation complète")) {
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
      setMessage("Documentation complète copiée. Vous pouvez la coller dans votre assistant.");
    } catch {
      setState("error");
      setMessage("La copie n'a pas abouti. Utilisez le lien de téléchargement ci-dessous.");
    }
  };
  return (
    <div className="not-prose my-4">
      <button
        type="button"
        onClick={copy}
        disabled={state === "loading"}
        className="rounded-lg border px-4 py-2 text-sm font-semibold disabled:opacity-60 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2"
        style={{ backgroundColor: "#76E7F4", color: "#092E33", borderColor: "#087E8B" }}
      >
        {state === "loading" ? "Copie en cours…" : state === "copied" ? "Documentation copiée ✓" : "Copier toute la documentation pour une IA"}
      </button>
      <p className="mt-2 text-sm" role="status" aria-live="polite">{message}</p>
      <a className="text-sm underline" href="https://raw.githubusercontent.com/mathieuworoniecki/marko-developer-docs/main/downloads/marko-documentation.json">Télécharger la documentation complète</a>
    </div>
  );
};
