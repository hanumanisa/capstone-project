/**
 * Normalizes a string by converting it to lowercase and removing all non-alphanumeric characters.
 */
export const norm = (str) => (str || '').replace(/[^a-zA-Z0-9]/g, '').toLowerCase();

/**
 * Calculates Levenshtein similarity between two strings.
 * Returns a value between 0.0 and 1.0.
 */
export const getLevenshteinSimilarity = (s1, s2) => {
    const len1 = s1.length;
    const len2 = s2.length;
    if (len1 === 0) return len2 === 0 ? 1.0 : 0.0;
    if (len2 === 0) return 0.0;

    const track = Array(len2 + 1).fill(null).map(() => Array(len1 + 1).fill(null));
    for (let i = 0; i <= len1; i += 1) track[0][i] = i;
    for (let j = 0; j <= len2; j += 1) track[j][0] = j;

    for (let j = 1; j <= len2; j += 1) {
        for (let i = 1; i <= len1; i += 1) {
            const indicator = s1[i - 1] === s2[j - 1] ? 0 : 1;
            track[j][i] = Math.min(
                track[j][i - 1] + 1, // deletion
                track[j - 1][i] + 1, // insertion
                track[j - 1][i - 1] + indicator // substitution
            );
        }
    }
    const distance = track[len2][len1];
    return 1.0 - (distance / Math.max(len1, len2));
};

/**
 * Checks if two normalized strings are similar based on Levenshtein distance
 * and prefix/suffix heuristics.
 */
export const isSimilar = (s1, s2) => {
    if (s1 === s2) return true;
    const sim = getLevenshteinSimilarity(s1, s2);
    if (sim >= 0.70) return true;
    if (s1.startsWith(s2) || s2.startsWith(s1) || s1.endsWith(s2) || s2.endsWith(s1)) {
        if (Math.abs(s1.length - s2.length) <= 3) {
            return true;
        }
    }
    return false;
};
