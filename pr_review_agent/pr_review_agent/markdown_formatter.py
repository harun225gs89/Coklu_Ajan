from collections import Counter

from pr_review_agent.models import ReviewResult


def render_markdown(review: ReviewResult) -> str:
    severity_counts = Counter(finding.severity for finding in review.findings)
    sections: list[str] = []
    sections.append("## PR Otomatik İnceleme Raporu")
    sections.append("")
    sections.append("### Özet")
    sections.append(f"- Toplam {len(review.findings)} bulgu bulundu.")
    sections.append(f"- Kritik: {severity_counts.get('critical', 0)}")
    sections.append(f"- Yüksek: {severity_counts.get('high', 0)}")
    sections.append(f"- Orta: {severity_counts.get('medium', 0)}")
    sections.append(f"- Düşük: {severity_counts.get('low', 0)}")
    sections.append(f"- Bilgi: {severity_counts.get('info', 0)}")
    sections.append("")

    categories = [
        ("logic", "### Mantık / Kod Kalitesi"),
        ("security", "### Güvenlik"),
        ("tests", "### Test Önerileri"),
    ]

    for category_key, heading in categories:
        relevant = [finding for finding in review.findings if finding.category == category_key]
        if not relevant:
            continue
        sections.append(heading)
        for finding in relevant:
            file_suffix = f"`{finding.file_path}`" if finding.file_path else "genel"
            sections.append(f"- [{finding.severity.upper()}] {finding.title} ({file_suffix})")
            sections.append(f"  - Açıklama: {finding.description}")
            sections.append(f"  - Kanıt: {finding.evidence}")
            sections.append(f"  - Öneri: {finding.recommendation}")
        sections.append("")

    if not review.findings:
        sections.append("### Bulgu yok")
        sections.append("- Mevcut diff'ten otomatik olarak anlamlı bir hata tespit edilemedi.")
        sections.append("")

    sections.append("### Sonuç")
    sections.append(review.recommendation or review.summary)
    return "\n".join(sections)
