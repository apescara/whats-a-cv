import type { ReactNode } from "react";

function inline(text: string): ReactNode[] {
  return text.split(/(\*\*[^*]+\*\*|`[^`]+`|\[[^\]]+\]\(https?:\/\/[^)\s]+\))/g).map((part, index) => {
    const link = part.match(/^\[([^\]]+)\]\((https?:\/\/[^)\s]+)\)$/);
    if (link) return <a key={index} href={link[2]} target="_blank" rel="noreferrer">{link[1]}</a>;
    if (part.startsWith("**") && part.endsWith("**")) return <strong key={index}>{part.slice(2, -2)}</strong>;
    if (part.startsWith("`") && part.endsWith("`")) return <code key={index}>{part.slice(1, -1)}</code>;
    return part;
  });
}

export default function MarkdownPreview({ content }: { content: string }) {
  const lines = content.replace(/^---\r?\n[\s\S]*?\r?\n---\r?\n?/, "").split(/\r?\n/); const blocks: ReactNode[] = [];
  const isBlock = (line: string, next = "") => /^(#{1,3}\s|[-*+]\s|\d+[.)]\s|>\s?|---$|\*\*\*$)/.test(line) || (line.includes("|") && /^\s*\|?\s*:?-{3,}/.test(next));
  for (let index = 0; index < lines.length;) {
    const line = lines[index];
    if (!line.trim() || /^<!--.*-->$/.test(line.trim())) { index++; continue; }
    const heading = line.match(/^(#{1,3})\s+(.+)$/);
    if (heading) { const body = inline(heading[2]); blocks.push(heading[1].length === 1 ? <h2 key={index}>{body}</h2> : heading[1].length === 2 ? <h3 key={index}>{body}</h3> : <h4 key={index}>{body}</h4>); index++; continue; }
    if (/^(---|\*\*\*)\s*$/.test(line)) { blocks.push(<hr key={index} />); index++; continue; }
    if (line.includes("|") && /^\s*\|?\s*:?-{3,}/.test(lines[index + 1] ?? "")) { const cells = (value: string) => value.trim().replace(/^\||\|$/g, "").split("|").map((cell) => cell.trim()); const headers = cells(line); index += 2; const rows: string[][] = []; while (index < lines.length && lines[index].includes("|")) rows.push(cells(lines[index++])); blocks.push(<div className="markdown-table-scroll" key={index}><table><thead><tr>{headers.map((header, cell) => <th key={cell}>{inline(header)}</th>)}</tr></thead><tbody>{rows.map((row, rowIndex) => <tr key={rowIndex}>{headers.map((_, cell) => <td key={cell}>{inline(row[cell] ?? "")}</td>)}</tr>)}</tbody></table></div>); continue; }
    const list = line.match(/^([-*+]|\d+[.)])\s+(.+)$/);
    if (list) { const ordered = /^\d/.test(list[1]); const items: ReactNode[] = []; while (index < lines.length) { const item = lines[index].match(ordered ? /^\d+[.)]\s+(.+)$/ : /^[-*+]\s+(.+)$/); if (!item) break; items.push(<li key={index}>{inline(item[1])}</li>); index++; } blocks.push(ordered ? <ol key={index}>{items}</ol> : <ul key={index}>{items}</ul>); continue; }
    if (line.startsWith(">")) { const quote: string[] = []; while (lines[index]?.startsWith(">")) quote.push(lines[index++].replace(/^>\s?/, "")); blocks.push(<blockquote key={index}>{inline(quote.join(" "))}</blockquote>); continue; }
    const paragraph: string[] = []; while (index < lines.length && lines[index].trim() && !isBlock(lines[index], lines[index + 1])) paragraph.push(lines[index++]); blocks.push(<p key={index}>{inline(paragraph.join(" "))}</p>);
  }
  return <div className="markdown-content">{blocks}</div>;
}
