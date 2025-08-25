const fs = require('fs');
const path = require('path');

// Function to extract text content from HTML, removing scripts and styles
function extractTextFromHtml(html) {
    // Remove script and style tags and their content
    let text = html.replace(/<script[^>]*>[\s\S]*?<\/script>/gi, '');
    text = text.replace(/<style[^>]*>[\s\S]*?<\/style>/gi, '');

    // Remove HTML tags
    text = text.replace(/<[^>]+>/g, ' ');

    // Decode HTML entities
    text = text.replace(/&nbsp;/g, ' ');
    text = text.replace(/&/g, '&');
    text = text.replace(/</g, '<');
    text = text.replace(/>/g, '>');
    text = text.replace(/"/g, '"');
    text = text.replace(/&#39;/g, "'");
    text = text.replace(/'/g, "'");

    // Clean up whitespace
    text = text.replace(/\s+/g, ' ').trim();

    return text;
}

// Function to extract title from HTML
function extractTitle(html) {
    const titleMatch = html.match(/<title[^>]*>([\s\S]*?)<\/title>/i);
    if (titleMatch) {
        return titleMatch[1].trim();
    }

    // Fallback: try to find h1
    const h1Match = html.match(/<h1[^>]*>([\s\S]*?)<\/h1>/i);
    if (h1Match) {
        return h1Match[1].replace(/<[^>]+>/g, '').trim();
    }

    return '';
}

// Function to extract description from HTML
function extractDescription(html) {
    // Try to find meta description
    const metaMatch = html.match(/<meta[^>]*name=["']description["'][^>]*content=["']([^"']*)[^>]*>/i);
    if (metaMatch) {
        return metaMatch[1].trim();
    }

    // Fallback: extract first paragraph or h2
    const pMatch = html.match(/<p[^>]*>([\s\S]*?)<\/p>/i);
    if (pMatch) {
        return pMatch[1].replace(/<[^>]+>/g, '').trim().substring(0, 300);
    }

    const h2Match = html.match(/<h2[^>]*>([\s\S]*?)<\/h2>/i);
    if (h2Match) {
        return h2Match[1].replace(/<[^>]+>/g, '').trim();
    }

    return '';
}

// Function to extract keywords from HTML
function extractKeywords(html) {
    // Try to find meta keywords
    const metaMatch = html.match(/<meta[^>]*name=["']keywords["'][^>]*content=["']([^"']*)[^>]*>/i);
    if (metaMatch) {
        return metaMatch[1].split(',').map(k => k.trim().toLowerCase());
    }

    // Extract common words from text (most frequent words)
    const text = extractTextFromHtml(html).toLowerCase();
    const words = text.match(/\b\w{4,}\b/g) || [];
    const wordCount = {};

    words.forEach(word => {
        if (!['that', 'with', 'this', 'will', 'your', 'from', 'they', 'know', 'want', 'been', 'good', 'much', 'some', 'time', 'very', 'when', 'come', 'here', 'just', 'like', 'long', 'make', 'many', 'over', 'such', 'take', 'than', 'them', 'well', 'were', 'what', 'year', 'could', 'have', 'there', 'these', 'where', 'which', 'while', 'about', 'would', 'their', 'after', 'before', 'being', 'every', 'never', 'other', 'should', 'under', 'also', 'because', 'between', 'doing', 'during', 'however', 'though', 'through', 'another', 'around', 'become', 'called', 'cannot', 'coming', 'enough', 'little', 'really', 'always', 'called', 'coming', 'enough', 'little', 'really', 'always', 'called', 'coming', 'enough', 'little', 'really'].includes(word)) {
            wordCount[word] = (wordCount[word] || 0) + 1;
        }
    });

    return Object.entries(wordCount)
        .sort(([,a], [,b]) => b - a)
        .slice(0, 20)
        .map(([word]) => word);
}

// Function to extract update date from HTML
function extractUpdateDate(html) {
    const dateMatch = html.match(/fecha\s+actualizacion:\s*([^<\n\r]+)/i);
    if (dateMatch) {
        return dateMatch[1].trim();
    }
    return null;
}

// Main function to generate index
function generateIndex() {
    const pildorasDir = path.join(__dirname, 'pildoras');
    const files = fs.readdirSync(pildorasDir);
    const htmlFiles = files.filter(file => file.endsWith('.html'));

    const indexData = {
        files: [],
        keywords: {},
        metadata: {
            created: new Date().toISOString(),
            description: "Índice de archivos HTML en la carpeta pildoras para búsquedas por palabras clave",
            version: "1.0",
            totalFiles: htmlFiles.length
        }
    };

    // Process each HTML file
    htmlFiles.forEach(file => {
        const filePath = path.join(pildorasDir, file);
        const html = fs.readFileSync(filePath, 'utf8');

        const archivo = file.replace('.html', '');
        const titulo = extractTitle(html);
        const descripcion = extractDescription(html);
        const palabrasClave = extractKeywords(html);
        const fechaActualizacion = extractUpdateDate(html);
        const ruta = `pildoras/${file}`;

        const fileData = {
            archivo,
            titulo,
            descripcion,
            palabrasClave,
            fechaActualizacion,
            ruta
        };

        indexData.files.push(fileData);

        // Build keyword index
        palabrasClave.forEach(keyword => {
            if (!indexData.keywords[keyword]) {
                indexData.keywords[keyword] = [];
            }
            indexData.keywords[keyword].push({
                archivo,
                titulo,
                relevancia: palabrasClave.indexOf(keyword) + 1
            });
        });
    });

    // Sort files alphabetically by title
    indexData.files.sort((a, b) => {
        const titleA = a.titulo || a.archivo;
        const titleB = b.titulo || b.archivo;
        return titleA.localeCompare(titleB);
    });

    // Write index file
    fs.writeFileSync('index_pildoras.json', JSON.stringify(indexData, null, 2), 'utf8');

    console.log(`Índice actualizado exitosamente. ${htmlFiles.length} archivos procesados.`);
    console.log(`Archivo generado: index_pildoras.json`);
}

// Run the generator
generateIndex();
