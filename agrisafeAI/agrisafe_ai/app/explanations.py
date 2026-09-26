from .risk_engine import RiskResult

ENGLISH_TEXT = {
    "Very high temperature increases heat exposure risk.": "Very high temperature increases heat exposure risk.",
    "High temperature increases heat exposure risk.": "High temperature increases heat exposure risk.",
    "High humidity combined with heat can reduce the body's ability to cool.": "High humidity combined with heat can reduce the body's ability to cool.",
    "Strong wind can increase spray drift risk.": "Strong wind can increase spray drift risk.",
    "Elevated wind can increase spray drift risk.": "Elevated wind can increase spray drift risk.",
    "High rain probability makes the planned spraying window unfavorable.": "High rain probability makes the planned spraying window unfavorable.",
    "Rain probability is elevated for a weather-sensitive spraying task.": "Rain probability is elevated for a weather-sensitive spraying task.",
    "Chemical identity and its label/SDS were not provided.": "Chemical identity and its label/SDS were not provided.",
    "The chemical could not be verified against the configured reference data.": "The chemical could not be verified against the configured reference data.",
    "Required PPE has not been confirmed as complete.": "Required PPE has not been confirmed as complete.",
    "Long prior outdoor exposure increases worker exposure risk.": "Long prior outdoor exposure increases worker exposure risk.",
    "Several hours of prior outdoor work increase exposure risk.": "Several hours of prior outdoor work increase exposure risk.",
    "High wind can make machinery and field operations more difficult.": "High wind can make machinery and field operations more difficult.",
    "Very high rain probability increases uncertainty for outdoor work.": "Very high rain probability increases uncertainty for outdoor work.",
    "No elevated risk factors were detected by the configured prototype rules.": "No elevated risk factors were detected by the configured prototype rules.",
    "Do not treat this assessment as a safe-to-proceed decision until the missing information is verified.": "Do not treat this assessment as a safe-to-proceed decision until the missing information is verified.",
    "Move the task to a cooler period and increase rest and hydration controls.": "Move the task to a cooler period and increase rest and hydration controls.",
    "Schedule breaks, hydration and a cooler work window.": "Schedule breaks, hydration and a cooler work window.",
    "Increase rest and hydration controls.": "Increase rest and hydration controls.",
    "Do not spray in strong wind. Reassess before starting.": "Do not spray in strong wind. Reassess before starting.",
    "Reassess wind immediately before spraying and follow the product label.": "Reassess wind immediately before spraying and follow the product label.",
    "Consider a later dry window and follow the product label for rain restrictions.": "Consider a later dry window and follow the product label for rain restrictions.",
    "Check the short-term forecast again immediately before spraying.": "Check the short-term forecast again immediately before spraying.",
    "Confirm all PPE required by the product label/SDS before starting.": "Confirm all PPE required by the product label/SDS before starting.",
    "Allow a recovery period before additional physically demanding outdoor work.": "Allow a recovery period before additional physically demanding outdoor work.",
    "Take a recovery break and reassess worker readiness.": "Take a recovery break and reassess worker readiness.",
    "Reassess operating conditions and follow equipment safety procedures.": "Reassess operating conditions and follow equipment safety procedures.",
    "Complete the standard farm safety checklist and follow the task SOP.": "Complete the standard farm safety checklist and follow the task SOP.",
    "Chemical hazard profile contributes 0 risk points.": "Chemical hazard profile contributes 0 risk points.",
}

MALAY_TEXT = {
    "Very high temperature increases heat exposure risk.": "Suhu yang sangat tinggi boleh meningkatkan risiko pendedahan haba.",
    "High temperature increases heat exposure risk.": "Suhu yang tinggi boleh meningkatkan risiko pendedahan haba.",
    "High humidity combined with heat can reduce the body's ability to cool.": "Kelembapan tinggi bersama suhu panas boleh mengurangkan keupayaan badan untuk menyejukkan diri.",
    "Strong wind can increase spray drift risk.": "Angin kuat boleh meningkatkan risiko semburan terbawa angin.",
    "Elevated wind can increase spray drift risk.": "Angin yang meningkat boleh meningkatkan risiko semburan terbawa angin.",
    "High rain probability makes the planned spraying window unfavorable.": "Kemungkinan hujan yang tinggi menjadikan masa penyemburan yang dirancang tidak sesuai.",
    "Rain probability is elevated for a weather-sensitive spraying task.": "Kemungkinan hujan meningkat untuk kerja penyemburan yang sensitif terhadap cuaca.",
    "Chemical identity and its label/SDS were not provided.": "Identiti bahan kimia serta label/SDSnya belum disediakan.",
    "The chemical could not be verified against the configured reference data.": "Bahan kimia tidak dapat disahkan berdasarkan data rujukan yang tersedia.",
    "Required PPE has not been confirmed as complete.": "PPE yang diperlukan belum disahkan lengkap.",
    "Long prior outdoor exposure increases worker exposure risk.": "Pendedahan luar yang lama sebelum ini meningkatkan risiko pekerja.",
    "Several hours of prior outdoor work increase exposure risk.": "Beberapa jam kerja luar sebelum ini meningkatkan risiko pendedahan.",
    "High wind can make machinery and field operations more difficult.": "Angin kuat boleh menjadikan operasi jentera dan kerja ladang lebih sukar.",
    "Very high rain probability increases uncertainty for outdoor work.": "Kemungkinan hujan yang sangat tinggi menambah ketidakpastian untuk kerja luar.",
    "No elevated risk factors were detected by the configured prototype rules.": "Tiada faktor risiko tinggi dikesan oleh peraturan prototaip yang ditetapkan.",
    "Do not treat this assessment as a safe-to-proceed decision until the missing information is verified.": "Jangan anggap penilaian ini selamat untuk diteruskan sehingga maklumat yang kurang disahkan.",
    "Move the task to a cooler period and increase rest and hydration controls.": "Pindahkan kerja ke waktu yang lebih sejuk dan tingkatkan kawalan rehat serta penghidratan.",
    "Schedule breaks, hydration and a cooler work window.": "Jadualkan rehat, penghidratan dan waktu kerja yang lebih sejuk.",
    "Increase rest and hydration controls.": "Tingkatkan kawalan rehat dan penghidratan.",
    "Do not spray in strong wind. Reassess before starting.": "Jangan sembur apabila angin kuat. Semak semula sebelum mula.",
    "Reassess wind immediately before spraying and follow the product label.": "Semak semula angin sejurus sebelum penyemburan dan ikut label produk.",
    "Consider a later dry window and follow the product label for rain restrictions.": "Pertimbangkan masa yang lebih kering dan ikut sekatan hujan pada label produk.",
    "Check the short-term forecast again immediately before spraying.": "Semak ramalan jangka pendek sekali lagi sebelum penyemburan.",
    "Confirm all PPE required by the product label/SDS before starting.": "Sahkan semua PPE yang diperlukan oleh label produk/SDS sebelum mula.",
    "Allow a recovery period before additional physically demanding outdoor work.": "Berikan masa pemulihan sebelum kerja luar yang lebih mencabar secara fizikal.",
    "Take a recovery break and reassess worker readiness.": "Ambil rehat pemulihan dan semak semula kesediaan pekerja.",
    "Reassess operating conditions and follow equipment safety procedures.": "Semak semula keadaan operasi dan ikut prosedur keselamatan peralatan.",
    "Complete the standard farm safety checklist and follow the task SOP.": "Lengkapkan senarai semak keselamatan ladang dan ikut SOP tugas.",
    "Chemical hazard profile contributes 0 risk points.": "Profil bahaya bahan kimia menyumbang 0 mata risiko.",
    "Chemical hazard profile contributes 10 risk points.": "Profil bahaya bahan kimia menyumbang 10 mata risiko.",
    "Chemical hazard profile contributes 15 risk points.": "Profil bahaya bahan kimia menyumbang 15 mata risiko.",
    "Chemical hazard profile contributes 20 risk points.": "Profil bahaya bahan kimia menyumbang 20 mata risiko.",
    "Chemical hazard profile contributes 25 risk points.": "Profil bahaya bahan kimia menyumbang 25 mata risiko.",
    "Chemical hazard profile contributes 30 risk points.": "Profil bahaya bahan kimia menyumbang 30 mata risiko.",
    "Chemical hazard profile contributes 35 risk points.": "Profil bahaya bahan kimia menyumbang 35 mata risiko.",
    "Chemical hazard profile contributes 40 risk points.": "Profil bahaya bahan kimia menyumbang 40 mata risiko.",
    "Chemical hazard profile contributes 45 risk points.": "Profil bahaya bahan kimia menyumbang 45 mata risiko.",
    "Chemical hazard profile contributes 50 risk points.": "Profil bahaya bahan kimia menyumbang 50 mata risiko.",
}

MULTILINE_TEXT = {
    "en": ENGLISH_TEXT,
    "ms": MALAY_TEXT,
}


def _translate_texts(texts, language):
    language = (language or "en").lower()
    mapping = MULTILINE_TEXT.get(language, ENGLISH_TEXT)
    translated = []
    for text in texts:
        translated_text = mapping.get(text)
        if translated_text is not None:
            translated.append(translated_text)
            continue
        if text.startswith("Chemical hazard profile contributes ") and text.endswith(" risk points."):
            try:
                number = text.split("Chemical hazard profile contributes ", 1)[1].split(" risk points.", 1)[0]
                translated.append(f"Profil bahaya bahan kimia menyumbang {number} mata risiko.")
            except ValueError:
                translated.append(text)
            continue
        translated.append(text)
    return translated


def translate_result(result: RiskResult, language: str = "en") -> RiskResult:
    return RiskResult(
        score=result.score,
        level=result.level,
        decision=result.decision,
        reasons=_translate_texts(result.reasons, language),
        actions=_translate_texts(result.actions, language),
        rules=result.rules,
        blockers=_translate_texts(result.blockers, language),
    )


def decision_summary(result, language: str = "en"):
    text = "Conditions are within the configured prototype thresholds. Complete the normal safety checklist before starting."
    if language == "ms":
        text = "Keadaan berada dalam had prototaip yang dikonfigurasikan. Lengkapkan senarai semak keselamatan biasa sebelum memulakan."
    if result.decision == "PROCEED":
        return text
    if result.decision == "MODIFY":
        text = "The task may be possible after applying the listed controls and reassessing conditions."
        if language == "ms":
            text = "Tugas mungkin boleh diteruskan selepas menggunakan kawalan yang disenaraikan dan menilai semula keadaan."
        return text
    if result.decision == "DELAY":
        text = "The current conditions are unfavorable. Wait for a safer window and reassess before starting."
        if language == "ms":
            text = "Keadaan semasa tidak sesuai. Tunggu masa yang lebih selamat dan nilai semula sebelum memulakan."
        return text
    text = "Do not rely on this assessment to proceed. Resolve the listed blockers or high-risk conditions first."
    if language == "ms":
        text = "Jangan bergantung pada penilaian ini untuk diteruskan. Selesaikan halangan yang disenaraikan atau keadaan berisiko tinggi terlebih dahulu."
    return text
