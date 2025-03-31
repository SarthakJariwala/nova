import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs) {
	return twMerge(clsx(inputs));
}

export function parseReferences(referencesText) {
	if (!referencesText) return [];

	// Use a regex that only matches the numbered list item patterns at the start of lines
	// This preserves the entire content of each reference
	const referenceLines = referencesText.split(/\n\s*(?=\d+\.\s+)/);

	// Process the first item which might not have a number prefix if it starts at the beginning
	const result = [];
	for (let i = 0; i < referenceLines.length; i++) {
			let line = referenceLines[i].trim();
			// If this is the first line and doesn't start with a number, skip it
			if (i === 0 && !line.match(/^\d+\.\s+/)) {
					continue;
			}
			result.push(line);
	}

	return result;
}