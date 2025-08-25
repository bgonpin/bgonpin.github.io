const fs = require('fs');

// Read the HTML file
const html = fs.readFileSync('pildoras/laps.html', 'utf8');

// Define the missing IDs that need to be added
const missingIds = [
    // Configuration section
    { tag: 'h3', text: 'Descargar e Instalar LAPS', id: 'descargar-laps' },
    { tag: 'h2', text: 'Descargar LAPS', id: 'descargar-laps-seccion' },
    { tag: 'h2', text: 'Instalar LAPS en el DC', id: 'instalar-dc' },
    { tag: 'h2', text: 'Configurar Directiva de Grupo para LAPS', id: 'configurar-gpo' },
    { tag: 'h2', text: 'Extender el Esquema de AD para LAPS', id: 'extender-esquema' },
    { tag: 'h2', text: 'Establecer Permisos de AD', id: 'permisos-ad' },
    { tag: 'h2', text: 'Desplegar LAPS a Máquinas Cliente', id: 'desplegar-clientes' },
    { tag: 'h2', text: 'Probar LAPS', id: 'probar-laps' },

    // Security section
    { tag: 'h2', text: 'Comprender el Modelo de Seguridad de LAPS:', id: 'modelo-seguridad' },
    { tag: 'h2', text: 'Añadir un nuevo usuario de dominio a la Máquina Cliente con Permiso AllExtendedRights.', id: 'permisos-usuario' },
    { tag: 'h3', text: 'Explicación: Todos los Derechos Extendidos:', id: 'explicacion-permisos' },

    // Exploitation section
    { tag: 'h2', text: 'Fase de Explotación', id: 'fase-explotacion' },
    { tag: 'h3', text: 'Bloodhound – Búsqueda de Permisos Débiles', id: 'bloodhound' },
    { tag: 'h4', text: 'Explicación de BloodHound', id: 'explicacion-bloodhound' },
    { tag: 'h2', text: 'Método de Explotación - Volcado de Credenciales (T1003)', id: 'metodo-explotacion' },
    { tag: 'h3', text: 'Impacket', id: 'impacket' },
    { tag: 'h3', text: 'Herramienta NXC', id: 'nxc' },
    { tag: 'h3', text: 'PyLaps', id: 'pylaps' },
    { tag: 'h3', text: 'LAPSDumper', id: 'lapsdumper' },
    { tag: 'h3', text: 'BloodyAD', id: 'bloodyad' },
    { tag: 'h3', text: 'Ldapsearch', id: 'ldapsearch' },
    { tag: 'h3', text: 'Metasploit: ldap_query', id: 'metasploit-ldap' },
    { tag: 'h3', text: 'Impacket-ntlmrelayx', id: 'ntlmrelayx' },
    { tag: 'h3', text: 'ldap_shell', id: 'ldap-shell' },

    // Windows exploitation
    { tag: 'h2', text: 'Explotación en Windows', id: 'explotacion-windows' },
    { tag: 'h3', text: 'PowerShell', id: 'powershell' },
    { tag: 'h3', text: 'NetTools', id: 'nettools' },
    { tag: 'h3', text: 'Sharplaps', id: 'sharplaps' },
    { tag: 'h3', text: 'Metasploit: enum_laps', id: 'metasploit-enum' },
    { tag: 'h3', text: 'Powerview', id: 'powerview' },
    { tag: 'h3', text: 'Explorador de Active Directory – Sysinternals', id: 'ad-explorer' },

    // Conclusion
    { tag: 'h2', text: 'Conclusión', id: 'conclusion' },
    { tag: 'h3', text: 'Mejores Prácticas para la Seguridad de LAPS:', id: 'mejores-practicas' },
    { tag: 'h3', text: 'Resumen de Puntos Clave', id: 'resumen-puntos' },
    { tag: 'h3', text: 'Notas', id: 'notas' },

    // Training programs
    { tag: 'h2', text: 'ÚNETE A NUESTROS PROGRAMAS DE ENTRENAMIENTO', id: 'programas-entrenamiento' },
    { tag: 'h3', text: 'PRINCIPIANTE', id: 'principiante' },
    { tag: 'h3', text: 'AVANZADO', id: 'avanzado' },
    { tag: 'h3', text: 'EXPERTO', id: 'experto' }
];

let updatedHtml = html;

// Process each missing ID
missingIds.forEach(({ tag, text, id }) => {
    // Create the regex pattern to find the tag with the specific text
    const pattern = new RegExp(`<${tag}>([^<]*${text}[^<]*)</${tag}>`, 'g');

    // Replace with the same tag but with id attribute
    updatedHtml = updatedHtml.replace(pattern, `<${tag} id="${id}">$1</${tag}>`);
});

// Write the updated HTML back to the file
fs.writeFileSync('pildoras/laps.html', updatedHtml, 'utf8');

console.log('All missing IDs have been added successfully!');
