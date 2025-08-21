// Lista de imágenes disponibles (sincronizada con archivos reales)
const imageFiles = [
    'IMG_6288.JPG', 'IMG_6290.JPG', 'IMG_6291.JPG', 'IMG_6295.JPG', 'IMG_6297.JPG',
    'IMG_6299.JPG', 'IMG_6300.JPG', 'IMG_6302.JPG', 'IMG_6303.JPG', 'IMG_6304.JPG',
    'IMG_6305.JPG', 'IMG_6306.JPG', 'IMG_6307.JPG', 'IMG_6308.JPG', 'IMG_6309.JPG',
    'IMG_6310.JPG', 'IMG_6311.JPG', 'IMG_6312 1.JPG', 'IMG_6312.JPG', 'IMG_6313.JPG',
    'IMG_6314.JPG', 'IMG_6315.JPG', 'IMG_6316.JPG', 'IMG_6317.JPG', 'IMG_6318.JPG',
    'IMG_6319.JPG', 'IMG_6320.JPG', 'IMG_6321.JPG', 'IMG_6323.JPG', 'IMG_6324.JPG',
    'IMG_6326.JPG', 'IMG_6327.JPG', 'IMG_6329.JPG', 'IMG_6330.JPG', 'IMG_6331.JPG',
    'IMG_6332.JPG', 'IMG_6333.JPG', 'IMG_6334.JPG', 'IMG_6335.JPG', 'IMG_6337.JPG',
    'IMG_6338.JPG', 'IMG_6339.JPG', 'IMG_6340.JPG', 'IMG_6341.JPG', 'IMG_6343.JPG',
    'IMG_6345.JPG', 'IMG_6346.JPG', 'IMG_6347.JPG', 'IMG_6348.JPG', 'IMG_6349.JPG',
    'IMG_6350.JPG', 'IMG_6351.JPG', 'IMG_6352.JPG', 'IMG_6353.JPG', 'IMG_6354.JPG',
    'IMG_6355.JPG', 'IMG_6363.JPG', 'IMG_6364.JPG', 'IMG_6365.JPG', 'IMG_6366.JPG',
    'IMG_6367.JPG', 'IMG_6368.JPG', 'IMG_6369.JPG', 'IMG_6370.JPG', 'IMG_6371.JPG',
    'IMG_6373.JPG', 'IMG_6374.JPG', 'IMG_6378.JPG', 'IMG_6379.JPG', 'IMG_6380.JPG',
    'IMG_6381.JPG', 'IMG_6383.JPG', 'IMG_6384.JPG', 'IMG_6385.JPG', 'IMG_6386.JPG',
    'IMG_6387.JPG', 'IMG_6388.JPG', 'IMG_6389.JPG', 'IMG_6391.JPG', 'IMG_6392.JPG',
    'IMG_6395.JPG', 'IMG_6396.JPG', 'IMG_6398.JPG', 'IMG_6399.JPG', 'IMG_6400.JPG',
    'IMG_6401.JPG', 'IMG_6402.JPG', 'IMG_6403.JPG', 'IMG_6410.JPG', 'IMG_6411.JPG',
    'IMG_6412.JPG', 'IMG_6414.JPG', 'IMG_6415.JPG', 'IMG_6416.JPG', 'IMG_6417.JPG',
    'IMG_6419.JPG', 'IMG_6420.JPG', 'IMG_6422.JPG', 'IMG_6428.JPG', 'IMG_6430.JPG',
    'IMG_6431.JPG', 'IMG_6432.JPG', 'IMG_6433.JPG', 'IMG_6434.JPG', 'IMG_6435.JPG',
    'IMG_6436.JPG', 'IMG_6437.JPG', 'IMG_6439.JPG', 'IMG_6440.JPG', 'IMG_6442.JPG',
    'IMG_6443.JPG', 'IMG_6446.JPG', 'IMG_6448.JPG', 'IMG_6452.JPG', 'IMG_6453.JPG',
    'IMG_6456.JPG', 'IMG_6458.JPG', 'IMG_6459.JPG', 'IMG_6460.JPG', 'IMG_6461.JPG',
    'IMG_6464.JPG', 'IMG_6465.JPG', 'IMG_6467.JPG', 'IMG_6468.JPG', 'IMG_6475.JPG',
    'IMG_6476.JPG', 'IMG_6477.JPG', 'IMG_6478.JPG', 'IMG_6479.JPG', 'IMG_6480.JPG',
    'IMG_6481.JPG', 'IMG_6484.JPG', 'IMG_6486.JPG', 'IMG_6487.JPG', 'IMG_6488.JPG',
    'IMG_6489.JPG', 'IMG_6494.JPG', 'IMG_6505.JPG', 'IMG_6507 1.JPG', 'IMG_6508.JPG',
    'IMG_20250821_111312.jpg', 'IMG_20250821_111314.jpg', 'IMG_20250821_111825.jpg',
    'IMG_20250821_111836.jpg', 'IMG_20250821_131409.jpg', 'IMG_20250821_131424.jpg',
    'IMG_20250821_131741.jpg', 'PXL_20250821_091837418.jpg', 'PXL_20250821_091854442.jpg',
    'PXL_20250821_091857601.jpg', 'PXL_20250821_093353445.jpg', 'PXL_20250821_101030819.jpg',
    'PXL_20250821_101047347.jpg', 'PXL_20250821_101139423.PANO.jpg', 'PXL_20250821_101302894.PANO.jpg',
    'PXL_20250821_101723585.PANO.jpg', 'PXL_20250821_101803350.PANO~2.jpg', 'PXL_20250821_102122664.jpg',
    'PXL_20250821_102834508.jpg', 'PXL_20250821_103159558.jpg', 'PXL_20250821_103257208.MP~2.jpg',
    'PXL_20250821_111853507.jpg', 'PXL_20250821_112307053.jpg', 'PXL_20250821_112309210.jpg'
];

// Descripciones divertidas y juveniles para las imágenes
const descriptions = [
    { title: "🌟 Momento Épico", desc: "¡Capturé este instante mágico que gritaba diversión!" },
    { title: "😎 Pose Legendaria", desc: "Con esta pose demostré que soy el rey/rey de las fotos" },
    { title: "🎨 Arte Vivo", desc: "Esta imagen es pura poesía visual, ¡incluso rimaría!" },
    { title: "✨ Chispa Mágica", desc: "La magia de este momento se siente hasta en los píxeles" },
    { title: "🎯 Instante Perfecto", desc: "Como diría mi abuela: '¡Esta foto es un 10!' 😘" },
    { title: "🌈 Colores Explosivos", desc: "Los colores aquí están más vivos que mi energía mañanera" },
    { title: "🔥 Fuego Interior", desc: "Esta imagen irradia más energía que un reactor nuclear" },
    { title: "💫 Estrella Fugaz", desc: "¡Este momento pasó volando como un unicornio en patineta!" },
    { title: "🎪 Circo de Emociones", desc: "Aquí las emociones danzan como payasos en una fiesta" },
    { title: "🌟 Aura Mística", desc: "Hay algo místico en esta imagen... ¡o quizás solo tengo hambre!" },
    { title: "🎨 Pintura Viva", desc: "Si esta imagen hablara, diría: '¡Yo soy arte!' 🎭" },
    { title: "💥 Explosión de Alegría", desc: "La felicidad aquí se siente como fuegos artificiales en el alma" },
    { title: "🌈 Arcoíris Emocional", desc: "Todos los colores del sentimiento en una sola imagen" },
    { title: "✨ Polvo de Hadas", desc: "Parece que las hadas hicieron una fiesta aquí mismo" },
    { title: "🎯 Blanco y Negro", desc: "No necesito colores para ser la foto más cool del álbum" },
    { title: "🌟 Luz Interior", desc: "Esta imagen ilumina más que una linterna en un apagón" },
    { title: "💫 Momento Estelar", desc: "Tan brillante que hasta las estrellas me envidian" },
    { title: "🎨 Canvas Vivo", desc: "Mi cara es el lienzo y las emociones son la pintura" },
    { title: "🔥 Fuego Sagrado", desc: "Aquí arde la pasión más intensa que un dragón enojado" },
    { title: "🌈 Espectro Visible", desc: "Todos mis estados de ánimo en una sola fotografía" }
];

// Variables globales
let currentImages = [];
let currentImageIndex = 0;
let isModalOpen = false;
let currentSlide = 0;
let autoPlayInterval = null;

// Elementos DOM
const modal = document.getElementById('imageModal');
const modalImage = document.getElementById('modalImage');
const modalTitle = document.getElementById('modalTitle');
const modalDesc = document.getElementById('modalDesc');

// Inicializar la aplicación
function init() {
    showLoadingScreen();
    setTimeout(() => {
        createImageObjects();
        renderGallery();
        setupEventListeners();
        hideLoadingScreen();
        showWelcomeMessage();
    }, 2500);
}

// Mostrar pantalla de carga
function showLoadingScreen() {
    const loadingScreen = document.getElementById('loadingScreen');
    loadingScreen.style.opacity = '1';
}

// Ocultar pantalla de carga
function hideLoadingScreen() {
    const loadingScreen = document.getElementById('loadingScreen');
    loadingScreen.style.opacity = '0';
    setTimeout(() => {
        loadingScreen.style.display = 'none';
    }, 500);
}

// Crear objetos de imagen con descripciones
function createImageObjects() {
    currentImages = imageFiles.map((file, index) => {
        const randomDesc = descriptions[Math.floor(Math.random() * descriptions.length)];
        return {
            id: index,
            filename: file,
            path: `imagenes/${encodeURIComponent(file)}`,
            title: randomDesc.title,
            description: randomDesc.desc,
            timestamp: Date.now() - (imageFiles.length - index) * 1000000
        };
    });
}

// Renderizar galería como carousel
function renderGallery() {
    const carousel = document.querySelector('.gallery-carousel');
    if (!carousel) return;

    carousel.innerHTML = '';

    if (currentImages.length === 0) {
        carousel.innerHTML = `
            <div style="text-align: center; padding: 60px; width: 100%;">
                <h2 style="margin-bottom: 20px;">🔍 ¡No se encontraron fotos!</h2>
                <p style="opacity: 0.7;">Intenta con otros términos de búsqueda</p>
            </div>
        `;
        updateSlideCounter();
        updateCarouselIndicators();
        return;
    }

    currentImages.forEach((image, index) => {
        const carouselItem = document.createElement('div');
        carouselItem.className = `carousel-item ${index === 0 ? 'active' : ''}`;
        carouselItem.dataset.index = index;

        carouselItem.innerHTML = `
            <img src="${image.path}" alt="${image.title}" loading="lazy" onerror="handleImageError(this)">
            <div class="image-overlay">
                <h3 class="image-title">${image.title}</h3>
                <p class="image-description">${image.description}</p>
            </div>
        `;

        // Agregar event listener para manejar errores de carga
        const img = carouselItem.querySelector('img');
        img.addEventListener('error', () => handleImageError(img));

        carouselItem.addEventListener('click', () => openModal(index));
        carousel.appendChild(carouselItem);
    });

    updateSlideCounter();
    updateCarouselIndicators();
    startAutoPlay();
}

// Actualizar contador de slides
function updateSlideCounter() {
    const currentSlideSpan = document.querySelector('.current-slide');
    const totalSlidesSpan = document.querySelector('.total-slides');

    if (currentSlideSpan && totalSlidesSpan) {
        currentSlideSpan.textContent = currentSlide + 1;
        totalSlidesSpan.textContent = currentImages.length || 1;
    }
}

// Actualizar indicadores del carousel
function updateCarouselIndicators() {
    const indicatorsContainer = document.querySelector('.carousel-indicators');
    if (!indicatorsContainer) return;

    indicatorsContainer.innerHTML = '';

    currentImages.forEach((_, index) => {
        const indicator = document.createElement('button');
        indicator.className = `indicator ${index === currentSlide ? 'active' : ''}`;
        indicator.onclick = () => goToSlide(index);
        indicatorsContainer.appendChild(indicator);
    });
}

// Funciones del carousel
function nextSlide() {
    if (currentImages.length === 0) return;
    currentSlide = (currentSlide + 1) % currentImages.length;
    updateCarousel();
}

function prevSlide() {
    if (currentImages.length === 0) return;
    currentSlide = (currentSlide - 1 + currentImages.length) % currentImages.length;
    updateCarousel();
}

function goToSlide(index) {
    currentSlide = index;
    updateCarousel();
}

function updateCarousel() {
    const items = document.querySelectorAll('.carousel-item');
    const indicators = document.querySelectorAll('.indicator');

    items.forEach((item, index) => {
        item.classList.toggle('active', index === currentSlide);
    });

    indicators.forEach((indicator, index) => {
        indicator.classList.toggle('active', index === currentSlide);
    });

    // Actualizar contador de slides
    updateSlideCounter();
}

function startAutoPlay() {
    if (autoPlayInterval) clearInterval(autoPlayInterval);
    autoPlayInterval = setInterval(nextSlide, 4000); // Cambiar cada 4 segundos
}

function stopAutoPlay() {
    if (autoPlayInterval) {
        clearInterval(autoPlayInterval);
        autoPlayInterval = null;
    }
}

// Alternar autoplay
function toggleAutoPlay() {
    const autoPlayBtn = document.querySelector('.auto-play-btn');
    const icon = autoPlayBtn.querySelector('i');

    if (autoPlayInterval) {
        stopAutoPlay();
        icon.className = 'fas fa-play';
        autoPlayBtn.title = 'Iniciar reproducción automática';
    } else {
        startAutoPlay();
        icon.className = 'fas fa-pause';
        autoPlayBtn.title = 'Pausar reproducción automática';
    }
}

// Configurar event listeners
function setupEventListeners() {
    // Modal
    document.querySelector('.close-modal').addEventListener('click', closeModal);

    // Botones del modal
    document.querySelector('.modal-controls .prev-btn').addEventListener('click', showPrevImage);
    document.querySelector('.modal-controls .next-btn').addEventListener('click', showNextImage);

    // Navegación por teclado
    document.addEventListener('keydown', (e) => {
        if (isModalOpen) {
            if (e.key === 'Escape') closeModal();
            if (e.key === 'ArrowLeft') showPrevImage();
            if (e.key === 'ArrowRight') showNextImage();
        }
    });

    // Cerrar modal haciendo click fuera
    modal.addEventListener('click', (e) => {
        if (e.target === modal) closeModal();
    });

    // Pausar autoplay cuando el usuario interactúa
    const carousel = document.querySelector('.gallery-carousel');
    if (carousel) {
        carousel.addEventListener('mouseenter', stopAutoPlay);
        carousel.addEventListener('mouseleave', startAutoPlay);
    }

    // Event listeners para búsqueda
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', performSearch);
        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                performSearch();
            }
        });
    }
}

// Mostrar mensaje de bienvenida
function showWelcomeMessage() {
    const welcome = document.createElement('div');
    welcome.style.cssText = `
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: var(--light-color);
        color: var(--dark-color);
        padding: 30px 40px;
        border-radius: var(--border-radius);
        box-shadow: var(--shadow-hover);
        z-index: 2000;
        text-align: center;
        border: 2px solid var(--primary-color);
    `;

    welcome.innerHTML = `
        <h2 style="margin: 0 0 15px 0; font-size: 1.5rem; color: var(--primary-color);">🎉 ¡Tordesillas 2025!</h2>
        <p style="margin: 0; font-size: 1rem; opacity: 0.8;">Explora nuestra galería de momentos inolvidables</p>
        <div style="margin-top: 20px; display: flex; gap: 10px; justify-content: center;">
            <span style="font-size: 1.5rem;">📸</span>
            <span style="font-size: 1.5rem;">🎊</span>
            <span style="font-size: 1.5rem;">💫</span>
        </div>
    `;

    document.body.appendChild(welcome);

    setTimeout(() => {
        welcome.style.opacity = '0';
        welcome.style.transition = 'opacity 0.5s ease-out';
        setTimeout(() => welcome.remove(), 500);
    }, 3000);
}

// Abrir modal
function openModal(index) {
    currentImageIndex = index;
    const image = currentImages[index];

    modalImage.src = image.path;
    modalImage.onerror = () => handleImageError(modalImage);
    modalTitle.textContent = image.title;
    modalDesc.textContent = image.description;

    modal.style.display = 'flex';
    isModalOpen = true;
    document.body.style.overflow = 'hidden';
    stopAutoPlay(); // Pausar autoplay cuando se abre el modal
}

// Cerrar modal
function closeModal() {
    modal.style.display = 'none';
    isModalOpen = false;
    document.body.style.overflow = 'auto';
    startAutoPlay(); // Reanudar autoplay cuando se cierra el modal
}

// Mostrar imagen anterior
function showPrevImage() {
    if (currentImages.length > 0) {
        currentImageIndex = (currentImageIndex - 1 + currentImages.length) % currentImages.length;
        updateModalImage();
    }
}

// Mostrar imagen siguiente
function showNextImage() {
    if (currentImages.length > 0) {
        currentImageIndex = (currentImageIndex + 1) % currentImages.length;
        updateModalImage();
    }
}

// Actualizar imagen en modal
function updateModalImage() {
    const image = currentImages[currentImageIndex];
    modalImage.src = image.path;
    modalImage.onerror = () => handleImageError(modalImage);
    modalTitle.textContent = image.title;
    modalDesc.textContent = image.description;
}

// Función para manejar errores de carga de imágenes
function handleImageError(img) {
    console.warn('Error al cargar imagen:', img.src);
    // Mostrar un placeholder o mensaje de error
    img.style.display = 'none';
    const errorDiv = document.createElement('div');
    errorDiv.style.cssText = `
        width: 100%;
        height: 500px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        background: var(--light-bg);
        border: 2px dashed var(--border-color);
        border-radius: var(--border-radius);
        color: var(--secondary-color);
        font-size: 1.1rem;
        text-align: center;
        padding: 20px;
    `;
    errorDiv.innerHTML = `
        <i class="fas fa-image" style="font-size: 3rem; margin-bottom: 15px; opacity: 0.5;"></i>
        <p style="margin: 0;">Imagen no disponible</p>
        <p style="font-size: 0.9rem; opacity: 0.7; margin: 5px 0 0 0;">Error al cargar la imagen</p>
    `;
    img.parentNode.insertBefore(errorDiv, img);
}

// Función para smooth scroll a anclas
function smoothScrollToAnchor() {
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
}

// Variables para búsqueda
let searchFilter = 'all';

// Función para realizar búsqueda
function performSearch() {
    const searchInput = document.getElementById('searchInput');
    const query = searchInput.value.trim().toLowerCase();

    if (query === '') {
        displaySearchResults(currentImages);
        return;
    }

    const filteredImages = currentImages.filter(image => {
        switch (searchFilter) {
            case 'title':
                return image.title.toLowerCase().includes(query);
            case 'description':
                return image.description.toLowerCase().includes(query);
            case 'all':
            default:
                return image.title.toLowerCase().includes(query) ||
                       image.description.toLowerCase().includes(query) ||
                       image.filename.toLowerCase().includes(query);
        }
    });

    displaySearchResults(filteredImages);
}

// Función para filtrar por tipo
function filterByType(type) {
    searchFilter = type;

    // Actualizar botones activos
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-filter="${type}"]`).classList.add('active');

    // Realizar búsqueda con el nuevo filtro
    performSearch();
}

// Función para mostrar resultados de búsqueda
function displaySearchResults(images) {
    const resultsContainer = document.getElementById('searchResults');

    if (images.length === 0) {
        resultsContainer.innerHTML = `
            <div class="no-results">
                <i class="fas fa-search"></i>
                <h3>No se encontraron resultados</h3>
                <p>Intenta con otros términos de búsqueda</p>
            </div>
        `;
        return;
    }

    const resultsHTML = images.map(image => `
        <div class="search-result-item" onclick="openModal(${image.id})">
            <img src="${image.path}" alt="${image.title}" onerror="handleImageError(this)">
            <div class="search-result-info">
                <div class="search-result-title">${image.title}</div>
                <div class="search-result-desc">${image.description}</div>
            </div>
        </div>
    `).join('');

    resultsContainer.innerHTML = resultsHTML;
}

// Iniciar la aplicación cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    smoothScrollToAnchor();
    init();
});
