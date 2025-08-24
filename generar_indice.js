const fs = require('fs');
const path = require('path');

// Función para filtrar archivos HTML (excluyendo .backup)
function filtrarArchivosHTML(directorio) {
    const archivos = fs.readdirSync(directorio);
    return archivos.filter(archivo => {
        return archivo.endsWith('.html') && !archivo.endsWith('.backup');
    });
}

// Función para extraer información de un archivo HTML
function extraerInfoHTML(rutaArchivo) {
    try {
        const contenido = fs.readFileSync(rutaArchivo, 'utf-8');
        const nombreArchivo = path.basename(rutaArchivo, '.html');

        // Extraer título
        const tituloMatch = contenido.match(/<title>(.*?)<\/title>/i);
        const titulo = tituloMatch ? tituloMatch[1].trim() : nombreArchivo;

        // Extraer la descripción principal (contenido de los párrafos)
        const parrafos = contenido.match(/<p[^>]*>(.*?)<\/p>/gi) || [];
        const textoPlano = parrafos.map(p => {
            // Remover etiquetas HTML y entidades
            return p.replace(/<[^>]*>/g, '').replace(/&[^;]+;/g, ' ').trim();
        }).join(' ').substring(0, 500); // Limitar a 500 caracteres

        // Extraer palabras clave del contenido
        const palabrasClave = extraerPalabrasClave(contenido + ' ' + titulo);

        // Extraer fecha de actualización si existe
        const fechaMatch = contenido.match(/Fecha actualizacion:\s*(\d{2}-\d{2}-\d{4})/i);
        const fechaActualizacion = fechaMatch ? fechaMatch[1] : null;

        return {
            archivo: nombreArchivo,
            titulo: titulo,
            descripcion: textoPlano,
            palabrasClave: palabrasClave,
            fechaActualizacion: fechaActualizacion,
            ruta: `pildoras/${path.basename(rutaArchivo)}`
        };
    } catch (error) {
        console.error(`Error procesando ${rutaArchivo}:`, error.message);
        return null;
    }
}

// Función para extraer palabras clave del contenido
function extraerPalabrasClave(contenido) {
    // Palabras comunes en español e inglés a excluir
    const palabrasComunes = new Set([
        'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas', 'y', 'o', 'pero', 'que', 'de', 'en', 'a', 'con',
        'por', 'para', 'es', 'son', 'está', 'están', 'ser', 'estar', 'tener', 'hacer', 'ir', 'ver', 'dar', 'saber',
        'querer', 'llegar', 'pasar', 'deber', 'poner', 'parecer', 'quedar', 'creer', 'hablar', 'llevar', 'dejar',
        'seguir', 'encontrar', 'llamar', 'venir', 'pensar', 'salir', 'volver', 'tomar', 'conocer', 'vivir', 'sentir',
        'tratar', 'mirar', 'contar', 'empezar', 'esperar', 'buscar', 'existir', 'entrar', 'trabajar', 'escribir',
        'perder', 'producir', 'ocurrir', 'entender', 'pedir', 'recibir', 'recordar', 'terminar', 'permitir', 'aparecer',
        'conseguir', 'comenzar', 'servir', 'sacar', 'necesitar', 'mantener', 'resultar', 'leer', 'caer', 'cambiar',
        'presentar', 'crear', 'abrir', 'considerar', 'oír', 'acabar', 'convertir', 'ganar', 'formar', 'traer',
        'partir', 'morir', 'aceptar', 'realizar', 'suponer', 'comprender', 'lograr', 'explicar', 'preguntar', 'tocar',
        'reconocer', 'estudiar', 'alcanzar', 'nacer', 'dirigir', 'correr', 'utilizar', 'pagar', 'ayudar', 'gustar',
        'jugar', 'escuchar', 'cumplir', 'ofrecer', 'descubrir', 'levantar', 'acercar', 'separar', 'recordar', 'acercarse',
        'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'an', 'a', 'is', 'are', 'was',
        'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
        'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
        'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'its', 'our', 'their', 'what', 'which', 'who', 'when',
        'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no',
        'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 'just', 'now', 'here', 'there', 'then',
        'once', 'always', 'never', 'sometimes', 'often', 'usually', 'seldom', 'rarely', 'again', 'also', 'as', 'even',
        'ever', 'far', 'long', 'near', 'much', 'many', 'little', 'few', 'well', 'better', 'best', 'worse', 'worst',
        'good', 'bad', 'new', 'old', 'young', 'big', 'small', 'large', 'short', 'tall', 'high', 'low', 'right', 'wrong'
    ]);

    // Limpiar el contenido y extraer palabras
    const textoLimpio = contenido
        .replace(/<[^>]*>/g, ' ') // Remover etiquetas HTML
        .replace(/&[^;]+;/g, ' ') // Remover entidades HTML
        .replace(/[^\w\s]/g, ' ') // Remover puntuación
        .toLowerCase()
        .split(/\s+/)
        .filter(palabra => {
            return palabra.length > 2 && // Al menos 3 caracteres
                   !palabrasComunes.has(palabra) &&
                   !/^\d+$/.test(palabra); // No solo números
        });

    // Contar frecuencia de palabras
    const frecuencia = {};
    textoLimpio.forEach(palabra => {
        frecuencia[palabra] = (frecuencia[palabra] || 0) + 1;
    });

    // Retornar las palabras más frecuentes (top 20)
    return Object.keys(frecuencia)
        .sort((a, b) => frecuencia[b] - frecuencia[a])
        .slice(0, 20);
}

// Función principal para generar el índice
function generarIndice() {
    const directorioPildoras = path.join(__dirname, 'pildoras');
    const archivosHTML = filtrarArchivosHTML(directorioPildoras);

    console.log(`Procesando ${archivosHTML.length} archivos HTML...`);

    const indice = {
        files: [],
        keywords: {},
        metadata: {
            created: new Date().toISOString(),
            description: "Índice de archivos HTML en la carpeta pildoras para búsquedas por palabras clave",
            version: "1.0",
            totalFiles: archivosHTML.length
        }
    };

    archivosHTML.forEach((archivo, index) => {
        console.log(`Procesando ${index + 1}/${archivosHTML.length}: ${archivo}`);
        const rutaCompleta = path.join(directorioPildoras, archivo);
        const info = extraerInfoHTML(rutaCompleta);

        if (info) {
            indice.files.push(info);

            // Indexar palabras clave
            info.palabrasClave.forEach(palabra => {
                if (!indice.keywords[palabra]) {
                    indice.keywords[palabra] = [];
                }
                indice.keywords[palabra].push({
                    archivo: info.archivo,
                    titulo: info.titulo,
                    relevancia: info.palabrasClave.indexOf(palabra) + 1
                });
            });
        }
    });

    // Guardar el índice
    const rutaIndice = path.join(__dirname, 'index_pildoras.json');
    fs.writeFileSync(rutaIndice, JSON.stringify(indice, null, 2), 'utf-8');

    console.log(`\nÍndice generado exitosamente en: ${rutaIndice}`);
    console.log(`Total de archivos procesados: ${indice.files.length}`);
    console.log(`Total de palabras clave indexadas: ${Object.keys(indice.keywords).length}`);
}

// Ejecutar si se llama directamente
if (require.main === module) {
    generarIndice();
}

module.exports = { generarIndice, filtrarArchivosHTML, extraerInfoHTML, extraerPalabrasClave };
