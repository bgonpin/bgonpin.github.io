// Navegación móvil
const hamburger = document.querySelector('.hamburger');
const navMenu = document.querySelector('.nav-menu');

hamburger.addEventListener('click', () => {
    hamburger.classList.toggle('active');
    navMenu.classList.toggle('active');
});

// Cerrar menú al hacer click en un enlace
document.querySelectorAll('.nav-link').forEach(n => n.addEventListener('click', () => {
    hamburger.classList.remove('active');
    navMenu.classList.remove('active');
}));

// Navegación suave
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Cambiar estilo de navbar al hacer scroll
window.addEventListener('scroll', () => {
    const navbar = document.querySelector('.navbar');
    if (window.scrollY > 50) {
        navbar.style.background = 'rgba(255, 255, 255, 0.98)';
        navbar.style.boxShadow = '0 2px 20px rgba(0,0,0,0.1)';
    } else {
        navbar.style.background = 'rgba(255, 255, 255, 0.95)';
        navbar.style.boxShadow = 'none';
    }
});

// Animación de barras de habilidades
const observerOptions = {
    threshold: 0.5,
    rootMargin: '0px 0px -100px 0px'
};

const skillsObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const skillBars = entry.target.querySelectorAll('.skill-progress');
            skillBars.forEach(bar => {
                const width = bar.getAttribute('data-width');
                setTimeout(() => {
                    bar.style.width = width + '%';
                }, 200);
            });
        }
    });
}, observerOptions);

const skillsSection = document.querySelector('.skills');
if (skillsSection) {
    skillsObserver.observe(skillsSection);
}

// Animación de elementos al hacer scroll
const fadeElements = document.querySelectorAll('.timeline-item, .project-card, .stat');

const fadeObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('fade-in', 'visible');
        }
    });
}, {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
});

fadeElements.forEach(element => {
    element.classList.add('fade-in');
    fadeObserver.observe(element);
});

// Contador animado para estadísticas
const animateCounters = () => {
    const counters = document.querySelectorAll('.stat h3');
    
    counters.forEach(counter => {
        const target = parseInt(counter.textContent.replace('+', ''));
        const increment = target / 100;
        let current = 0;
        
        const updateCounter = () => {
            if (current < target) {
                current += increment;
                counter.textContent = Math.ceil(current) + '+';
                requestAnimationFrame(updateCounter);
            } else {
                counter.textContent = target + '+';
            }
        };
        
        updateCounter();
    });
};

// Observer para las estadísticas
const statsObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            animateCounters();
            statsObserver.unobserve(entry.target);
        }
    });
}, { threshold: 0.5 });

const statsSection = document.querySelector('.stats');
if (statsSection) {
    statsObserver.observe(statsSection);
}

// Sección de contacto simplificada - solo información de contacto

// Validación de email
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Sistema de notificaciones
function showNotification(message, type = 'info') {
    // Crear elemento de notificación
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // Estilos de la notificación
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        color: white;
        font-weight: 500;
        z-index: 10000;
        transform: translateX(400px);
        transition: transform 0.3s ease;
        max-width: 300px;
        word-wrap: break-word;
    `;
    
    // Colores según el tipo
    switch (type) {
        case 'success':
            notification.style.background = '#28a745';
            break;
        case 'error':
            notification.style.background = '#dc3545';
            break;
        default:
            notification.style.background = '#667eea';
    }
    
    // Agregar al DOM
    document.body.appendChild(notification);
    
    // Animar entrada
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Remover después de 5 segundos
    setTimeout(() => {
        notification.style.transform = 'translateX(400px)';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 5000);
}

// Efecto parallax sutil en el hero
window.addEventListener('scroll', () => {
    const scrolled = window.pageYOffset;
    const hero = document.querySelector('.hero');
    if (hero) {
        hero.style.transform = `translateY(${scrolled * 0.5}px)`;
    }
});

// Indicador de scroll
const scrollIndicator = document.querySelector('.scroll-indicator');
if (scrollIndicator) {
    scrollIndicator.addEventListener('click', () => {
        document.querySelector('#about').scrollIntoView({
            behavior: 'smooth'
        });
    });
    
    // Ocultar indicador al hacer scroll
    window.addEventListener('scroll', () => {
        if (window.scrollY > 100) {
            scrollIndicator.style.opacity = '0';
        } else {
            scrollIndicator.style.opacity = '0.7';
        }
    });
}

// Funcionalidad del mensaje de noticias en JavaScript
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM cargado, mostrando mensaje de noticias...');

    // Mostrar mensaje después de 3 segundos
    setTimeout(() => {
        mostrarMensajeNoticias();
    }, 3000);
});

// Mostrar mensaje de últimas noticias
function mostrarMensajeNoticias() {
    const mensaje = `
📰 ¡BIENVENIDO! Últimas Novedades del Sitio 📰

📚 NUEVO CONTENIDO DISPONIBLE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔐 SSH - Protocolo Seguro:
¿Quieres aprender sobre SSH? Descubre este protocolo fundamental para seguridad en redes.

⚡ Integración Wazuh + VirusTotal:
Tutorial avanzado sobre detección de malware usando estas poderosas herramientas.

🤖 Google Fotos con IA:
Explora las nuevas funciones de IA para edición de fotos y animaciones.

🛡️ EDR - Endpoint Detection & Response:
Todo sobre ciberseguridad avanzada en dispositivos finales.

🐍 YARA + Python para Malware:
Sistema automatizado de detección de amenazas usando reglas YARA.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 DISFRUTA TU VISITA Y EXPLORA NUESTRO CONTENIDO!

¿Quieres aprender más sobre estos temas?

● Píldoras Técnicas
● Tutoriales Avanzados
● Herramientas de IA
● Ciberseguridad Actual
● Automatización con Python

📖 Visita nuestras secciones para contenido detallado
    `;

    alert(mensaje);

    console.log('Mensaje de noticias mostrado correctamente');
}

// Mostrar popup de ventana con últimas noticias
function mostrarPopupVentana() {
    console.log('Mostrando popup de ventana...');

    // Crear contenido HTML para el popup
    const popupContent = `
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📰 Últimas Novedades - Benito González Piñeiro</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body {
            font-family: 'Times New Roman', serif;
            background-color: #f8f9fa;
            color: #2c3e50;
            line-height: 1.6;
        }
        .news-item {
            transition: all 0.3s ease;
        }
        .news-item:hover {
            background-color: #f8f9fa !important;
            transform: translateY(-2px);
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .news-list {
            max-height: 600px;
            overflow-y: auto;
        }
        .header-bg {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            text-align: center;
        }
        .close-btn {
            position: fixed;
            top: 10px;
            right: 10px;
            background: #dc3545;
            color: white;
            border: none;
            padding: 8px 12px;
            border-radius: 5px;
            cursor: pointer;
            z-index: 1000;
        }
        .news-link {
            color: #0932af;
            text-decoration: none;
            font-weight: 600;
        }
        .news-link:hover {
            color: #061f7f;
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <button class="close-btn" onclick="window.close()">X Cerrar</button>

    <div class="header-bg">
        <h2><i class="fas fa-newspaper"></i> Últimas Novedades del Sitio</h2>
        <p>Descubre las últimas actualizaciones en mis conocimientos</p>
    </div>

    <div class="container-fluid mt-4">
        <div id="newsContent">
            <div class="text-center mb-4">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Cargando...</span>
                </div>
                <p class="mt-2">Cargando contenido...</p>
            </div>
        </div>
    </div>

    <div class="text-center mt-4 pb-4">
        <a href="index.html" class="btn btn-primary" target="_parent">
            <i class="fas fa-home me-2"></i>Ir al Sitio Principal
        </a>
        <button onclick="window.close()" class="btn btn-secondary ms-2">
            <i class="fas fa-times me-2"></i>Cerrar Ventana
        </button>
    </div>

    <script>
        // Datos de ejemplo de últimas novedades (hardcoded para evitar problemas de CORS)
        const ultimasNovedades = [
            {
                titulo: "¿Qué es SSH?",
                descripcion: "SSH, que significa \"Secure Shell\" (en español, \"Consola Segura\"), es un protocolo de red y un conjunto de utilidades...",
                enlace: "pildoras/ssh.html",
                tipo: "Píldora Técnica"
            },
            {
                titulo: "Análisis Técnico: Integración de VirusTotal en Plataformas Wazuh",
                descripcion: "Metodología para la Detección Avanzada de Malware mediante Inteligencia de Amenazas...",
                enlace: "pildoras/wazuh-virus-total.html",
                tipo: "Tutorial Avanzado"
            },
            {
                titulo: "Google potencia Google Fotos con nuevas herramientas de IA",
                descripcion: "La app evoluciona con funciones para animar fotos, eliminar elementos y aplicar estilos artísticos...",
                enlace: "pildoras/google-fotos-herramientas-ia.html",
                tipo: "Herramientas IA"
            },
            {
                titulo: "EDR (Endpoint Detection and Response)",
                descripcion: "Un EDR es una solución que monitorea, detecta y responde a actividades malintencionadas en endpoints...",
                enlace: "pildoras/edr.html",
                tipo: "Ciberseguridad"
            },
            {
                titulo: "Sistema de Detección de Malware con YARA",
                descripcion: "Análisis automatizado de archivos mediante reglas YARA y base de datos MongoDB...",
                enlace: "pildoras/yara_python.html",
                tipo: "Python & Malware"
            }
        ];

        // Cargar contenidos
        document.addEventListener('DOMContentLoaded', function() {
            cargarNovedades();
        });

        function cargarNovedades() {
            const newsContent = document.getElementById('newsContent');
            let html = '<div class="row justify-content-center"><div class="col-lg-10">';

            ultimasNovedades.forEach((noticia, index) => {
                html += \`
                <div class="news-item card mb-3">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <h5 class="card-title">
                                <a href="\${noticia.enlace}" class="news-link" target="_parent">\${noticia.titulo}</a>
                            </h5>
                            <span class="badge bg-primary">\${noticia.tipo}</span>
                        </div>
                        <p class="card-text text-muted">\${noticia.descripcion}</p>
                        <div class="text-end">
                            <small class="text-muted">
                                <i class="fas fa-calendar-alt me-1"></i>Publicado recientemente
                            </small>
                        </div>
                    </div>
                </div>
                \`;
            });

            html += '</div></div></div>';
            newsContent.innerHTML = html;
        }

        // Auto-cerrar después de 30 segundos
        setTimeout(() => {
            if (confirm('¿Deseas cerrar esta ventana emergente?')) {
                window.close();
            }
        }, 30000);
    </script>
</body>
</html>
    `;

    // Abrir popup ventana
    try {
        const popup = window.open('', 'novedadesPopup', 'width=900,height=700,resizable=yes,scrollbars=yes,status=yes');
        if (popup) {
            popup.document.write(popupContent);
            popup.focus();

            console.log('Popup de ventana abierta correctamente');
        } else {
            console.log('Popup bloqueado por el navegador');
            alert('Parece que tu navegador bloqueó la ventana emergente. Permite popups para este sitio.');
        }
    } catch (error) {
        console.error('Error abriendo popup:', error);
        alert('Hubo un problema abriendo el popup. Verifica que los popups estén permitidos.');
    }
}

// Agregar modal de noticias al DOM inmediatamente
function agregarModalEstaticamente() {
    const modalHtml = `
    <div class="modal fade" id="newsModal" tabindex="-1" aria-labelledby="newsModalLabel" aria-hidden="true">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header bg-primary text-white">
                    <h1 class="modal-title fs-5" id="newsModalLabel">📰 Últimas Novedades del Sitio</h1>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <div id="newsList" class="news-list">
                        <div class="text-center">
                            <div class="spinner-border text-primary" role="status">
                                <span class="visually-hidden">Cargando...</span>
                            </div>
                            <p class="mt-2 text-muted">Cargando últimas novedades...</p>
                        </div>
                    </div>
                    <div class="mt-3 text-end">
                        <small class="text-muted">Estás viendo las últimas actualizaciones de contenido.</small>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
                    <a href="pildoras/pildoras.html" class="btn btn-primary" target="_blank">
                        <i class="fas fa-eye me-1"></i>Ver Todas las Píldoras
                    </a>
                </div>
            </div>
        </div>
    </div>
    `;

    document.body.insertAdjacentHTML('beforeend', modalHtml);
}

// Mostrar popup de últimas noticias
function mostrarPopupNoticias() {
    console.log('Intentando mostrar popup de noticias...');
    console.log('Bootstrap disponible:', typeof bootstrap);

    // Verificar si Bootstrap está disponible
    if (typeof bootstrap === 'undefined') {
        console.log('Bootstrap no disponible, esperando...');
        setTimeout(() => mostrarPopupNoticias(), 100);
        return;
    }

    const newsModalEl = document.getElementById('newsModal');
    if (!newsModalEl) {
        console.error('Modal no encontrado');
        console.log('Elementos en body:', document.body.innerHTML.substring(0, 500));
        return;
    }

    console.log('Modal encontrado, inicializando...');

    try {
        // Inicializar modal de Bootstrap
        const newsModal = new bootstrap.Modal(newsModalEl, {
            backdrop: 'static',
            keyboard: true
        });

        console.log('Modal inicializado, cargando datos...');

        // Cargar y mostrar noticias
        cargarUltimosPildoras();

        // Mostrar modal después de un breve delay
        setTimeout(() => {
            console.log('Mostrando modal...');
            newsModal.show();
        }, 500);

    } catch (error) {
        console.error('Error inicializando modal:', error);
        // Fallback: mostrar un alert simple
        alert('¡Bienvenido! Descubre las últimas novedades en nuestras Píldoras.');
    }
}

// Cargar últimos pildoras del JSON
async function cargarUltimosPildoras() {
    try {
        const response = await fetch('index_pildoras.json');
        const data = await response.json();

        const newsList = document.getElementById('newsList');
        newsList.innerHTML = '';

        // Obtener los últimos 5 pildoras más "recientes" (asumiendo orden por título o algo, ya que fechas son null)
        const pildoras = data.files;
        // Tomar los primeros 5 como ejemplo, o filtrar por actualizados
        const ultimos = pildoras.filter(p => p.archivo.includes('ssh') || p.archivo.includes('wazuh') || p.archivo.includes('google') || p.archivo.includes('lamehug') || p.archivo.includes('notebooklm')).slice(0, 5);

        if (ultimos.length === 0) {
            // Si no hay recientes, mostrar algunos destacados
            ultimos.push(...pildoras.slice(0, 5));
        }

        ultimos.forEach((item, index) => {
            const newsItem = document.createElement('div');
            newsItem.className = 'news-item mb-3 p-3 border rounded';
            newsItem.innerHTML = `
                <h6 class="text-primary fw-bold mb-2">
                    <a href="${item.ruta}" class="text-decoration-none" target="_blank">${item.titulo}</a>
                </h6>
                <p class="mb-1 text-muted">${item.descripcion.substring(0, 120)}...</p>
                <small class="text-secondary">
                    <i class="fas fa-calendar-alt me-1"></i>Publicado recientemente
                </small>
            `;
            newsList.appendChild(newsItem);
        });

    } catch (error) {
        console.error('Error cargando noticias:', error);
        const newsList = document.getElementById('newsList');
        newsList.innerHTML = `
            <div class="alert alert-info">
                <i class="fas fa-info-circle me-2"></i>
                No se pudieron cargar las últimas novedades. ¡Visita nuestras píldoras para contenido actualizado!
            </div>
        `;
    }
}

// Manejo de errores de imágenes
document.querySelectorAll('img').forEach(img => {
    img.addEventListener('error', function() {
        this.style.display = 'none';
    });
});

// Mejoras de accesibilidad
document.addEventListener('keydown', (e) => {
    // Navegación con teclado para el menú móvil
    if (e.key === 'Escape' && navMenu.classList.contains('active')) {
        hamburger.classList.remove('active');
        navMenu.classList.remove('active');
    }
});

// Detectar preferencias de movimiento reducido
const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

if (prefersReducedMotion.matches) {
    // Deshabilitar animaciones si el usuario prefiere movimiento reducido
    document.documentElement.style.setProperty('--animation-duration', '0.01ms');
}

console.log('🚀 Portfolio cargado correctamente');
console.log('💼 Benito González Piñeiro - Especialista en Sistemas e IA');
