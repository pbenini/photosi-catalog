/**
 * Graph zoom and pan functionality for service graphs.
 * Implements a lightweight JavaScript solution for zooming and panning the service graphs.
 */

class GraphZoomPan {
    constructor(containerId, options = {}) {
        // Get the container element
        this.container = document.getElementById(containerId);
        if (!this.container) {
            console.error(`Container with ID '${containerId}' not found`);
            return;
        }

        // Default options
        this.options = {
            minScale: 0.3,         // Minimum zoom scale
            maxScale: 3,           // Maximum zoom scale
            zoomFactor: 0.1,       // How much to zoom on each wheel event
            wheelZoomEnabled: true, // Enable mouse wheel zoom
            dragPanEnabled: true,   // Enable drag to pan
            ...options
        };

        // Create the transform container
        this.createTransformContainer();

        // Current transformation state
        this.state = {
            scale: 1,
            offsetX: 0,
            offsetY: 0,
            isDragging: false,
            lastMouseX: 0,
            lastMouseY: 0
        };

        // Create controls container
        this.createControls();

        // Initial apply of transform
        this.applyTransform();

        // Set up event listeners
        this.setupEventListeners();
    }

    /**
     * Create a wrapper container for all graph content
     */
    createTransformContainer() {
        // Get all child elements of the container
        const children = Array.from(this.container.children);
        
        // Create transform container
        this.transformContainer = document.createElement('div');
        this.transformContainer.className = 'graph-transform-container';
        this.transformContainer.style.position = 'absolute';
        this.transformContainer.style.top = '0';
        this.transformContainer.style.left = '0';
        this.transformContainer.style.width = '100%';
        this.transformContainer.style.height = '100%';
        this.transformContainer.style.transformOrigin = '0 0';
        
        // Move all children to the transform container
        children.forEach(child => {
            // Skip the controls if they exist
            if (child.className === 'graph-controls') return;
            this.transformContainer.appendChild(child);
        });
        
        // Add the transform container to the main container
        this.container.appendChild(this.transformContainer);
    }

    /**
     * Create zoom control buttons
     */
    createControls() {
        // Create controls container
        const controls = document.createElement('div');
        controls.className = 'graph-controls';
        controls.style.position = 'absolute';
        controls.style.top = '10px';
        controls.style.right = '10px';
        controls.style.zIndex = '100';
        controls.style.display = 'flex';
        controls.style.gap = '5px';
        controls.style.backgroundColor = 'rgba(255, 255, 255, 0.8)';
        controls.style.padding = '5px';
        controls.style.borderRadius = '4px';
        controls.style.boxShadow = '0 2px 5px rgba(0, 0, 0, 0.1)';

        // Zoom in button
        const zoomInBtn = document.createElement('button');
        zoomInBtn.innerHTML = '+';
        zoomInBtn.title = 'Zoom In';
        zoomInBtn.style.width = '30px';
        zoomInBtn.style.height = '30px';
        zoomInBtn.style.cursor = 'pointer';
        zoomInBtn.style.borderRadius = '3px';
        zoomInBtn.style.backgroundColor = '#fff';
        zoomInBtn.style.border = '1px solid #ddd';
        zoomInBtn.style.fontSize = '16px';
        zoomInBtn.style.fontWeight = 'bold';
        zoomInBtn.addEventListener('click', () => this.zoom(this.options.zoomFactor));

        // Zoom out button
        const zoomOutBtn = document.createElement('button');
        zoomOutBtn.innerHTML = '−';
        zoomOutBtn.title = 'Zoom Out';
        zoomOutBtn.style.width = '30px';
        zoomOutBtn.style.height = '30px';
        zoomOutBtn.style.cursor = 'pointer';
        zoomOutBtn.style.borderRadius = '3px';
        zoomOutBtn.style.backgroundColor = '#fff';
        zoomOutBtn.style.border = '1px solid #ddd';
        zoomOutBtn.style.fontSize = '16px';
        zoomOutBtn.style.fontWeight = 'bold';
        zoomOutBtn.addEventListener('click', () => this.zoom(-this.options.zoomFactor));

        // Reset button
        const resetBtn = document.createElement('button');
        resetBtn.innerHTML = '⟲';
        resetBtn.title = 'Reset View';
        resetBtn.style.width = '30px';
        resetBtn.style.height = '30px';
        resetBtn.style.cursor = 'pointer';
        resetBtn.style.borderRadius = '3px';
        resetBtn.style.backgroundColor = '#fff';
        resetBtn.style.border = '1px solid #ddd';
        resetBtn.style.fontSize = '16px';
        resetBtn.addEventListener('click', () => this.reset());

        // Add buttons to controls
        controls.appendChild(zoomInBtn);
        controls.appendChild(zoomOutBtn);
        controls.appendChild(resetBtn);

        // Add controls to container
        this.container.appendChild(controls);
    }

    /**
     * Set up all event listeners
     */
    setupEventListeners() {
        // Mouse wheel zoom
        if (this.options.wheelZoomEnabled) {
            this.container.addEventListener('wheel', this.handleWheel.bind(this), { passive: false });
        }

        // Drag to pan
        if (this.options.dragPanEnabled) {
            this.container.addEventListener('mousedown', this.handleMouseDown.bind(this));
            document.addEventListener('mousemove', this.handleMouseMove.bind(this));
            document.addEventListener('mouseup', this.handleMouseUp.bind(this));
            
            // Touch events for mobile
            this.container.addEventListener('touchstart', this.handleTouchStart.bind(this));
            document.addEventListener('touchmove', this.handleTouchMove.bind(this));
            document.addEventListener('touchend', this.handleTouchEnd.bind(this));
        }

        // Window resize
        window.addEventListener('resize', this.handleResize.bind(this));
    }

    /**
     * Apply the current transform to the transform container
     */
    applyTransform() {
        const transform = `translate(${this.state.offsetX}px, ${this.state.offsetY}px) scale(${this.state.scale})`;
        this.transformContainer.style.transform = transform;
    }

    /**
     * Zoom the graph by the given delta amount
     * @param {number} delta - Positive to zoom in, negative to zoom out
     */
    zoom(delta) {
        const oldScale = this.state.scale;
        const newScale = Math.max(
            this.options.minScale,
            Math.min(this.options.maxScale, oldScale + delta)
        );
        
        if (oldScale !== newScale) {
            // Get the container center point
            const containerRect = this.container.getBoundingClientRect();
            const centerX = containerRect.width / 2;
            const centerY = containerRect.height / 2;
            
            // Adjust the offset to zoom toward the center
            const scaleFactor = newScale / oldScale;
            this.state.offsetX = centerX + (this.state.offsetX - centerX) * scaleFactor;
            this.state.offsetY = centerY + (this.state.offsetY - centerY) * scaleFactor;
            this.state.scale = newScale;
            
            this.applyTransform();
        }
    }

    /**
     * Reset the graph to its initial state
     */
    reset() {
        this.state.scale = 1;
        this.state.offsetX = 0;
        this.state.offsetY = 0;
        this.applyTransform();
    }

    /**
     * Handle mouse wheel events for zooming
     * @param {WheelEvent} event - The wheel event
     */
    handleWheel(event) {
        event.preventDefault();
        
        // Determine zoom direction
        const delta = event.deltaY < 0 ? this.options.zoomFactor : -this.options.zoomFactor;
        
        // Get mouse position for zooming toward cursor
        const rect = this.container.getBoundingClientRect();
        const mouseX = event.clientX - rect.left;
        const mouseY = event.clientY - rect.top;
        
        const oldScale = this.state.scale;
        const newScale = Math.max(
            this.options.minScale,
            Math.min(this.options.maxScale, oldScale + delta)
        );
        
        if (oldScale !== newScale) {
            // Calculate zoom based on cursor position
            const scaleFactor = newScale / oldScale;
            this.state.offsetX = mouseX + (this.state.offsetX - mouseX) * scaleFactor;
            this.state.offsetY = mouseY + (this.state.offsetY - mouseY) * scaleFactor;
            this.state.scale = newScale;
            
            this.applyTransform();
        }
    }

    /**
     * Handle mouse down event to start dragging
     * @param {MouseEvent} event - The mouse event
     */
    handleMouseDown(event) {
        // Only handle left mouse button
        if (event.button !== 0) return;
        
        // Don't drag if clicking on a control button
        if (event.target.closest('.graph-controls')) return;
        
        this.state.isDragging = true;
        this.state.lastMouseX = event.clientX;
        this.state.lastMouseY = event.clientY;
        this.container.style.cursor = 'grabbing';
        
        // Prevent default to avoid text selection
        event.preventDefault();
    }

    /**
     * Handle mouse move event while dragging
     * @param {MouseEvent} event - The mouse event
     */
    handleMouseMove(event) {
        if (!this.state.isDragging) return;
        
        const deltaX = event.clientX - this.state.lastMouseX;
        const deltaY = event.clientY - this.state.lastMouseY;
        
        this.state.offsetX += deltaX;
        this.state.offsetY += deltaY;
        
        this.state.lastMouseX = event.clientX;
        this.state.lastMouseY = event.clientY;
        
        this.applyTransform();
    }

    /**
     * Handle mouse up event to stop dragging
     */
    handleMouseUp() {
        if (this.state.isDragging) {
            this.state.isDragging = false;
            this.container.style.cursor = 'grab';
        }
    }

    /**
     * Handle touch start event for mobile
     * @param {TouchEvent} event - The touch event
     */
    handleTouchStart(event) {
        // Don't start drag if touching a control
        if (event.target.closest('.graph-controls')) return;
        
        if (event.touches.length === 1) {
            this.state.isDragging = true;
            this.state.lastMouseX = event.touches[0].clientX;
            this.state.lastMouseY = event.touches[0].clientY;
            
            // Prevent default to avoid scrolling
            event.preventDefault();
        }
    }

    /**
     * Handle touch move event for mobile
     * @param {TouchEvent} event - The touch event
     */
    handleTouchMove(event) {
        if (!this.state.isDragging || event.touches.length !== 1) return;
        
        event.preventDefault();
        
        const deltaX = event.touches[0].clientX - this.state.lastMouseX;
        const deltaY = event.touches[0].clientY - this.state.lastMouseY;
        
        this.state.offsetX += deltaX;
        this.state.offsetY += deltaY;
        
        this.state.lastMouseX = event.touches[0].clientX;
        this.state.lastMouseY = event.touches[0].clientY;
        
        this.applyTransform();
    }

    /**
     * Handle touch end event for mobile
     */
    handleTouchEnd() {
        this.state.isDragging = false;
    }

    /**
     * Handle window resize
     */
    handleResize() {
        // Re-apply transform on resize
        this.applyTransform();
    }
}


// Initialize the graph zoom/pan functionality
function initializeGraphZoomPan(containerId, options = {}) {
    const container = document.getElementById(containerId);
    if (!container) return null;
    
    // Add grab cursor to indicate draggability
    container.style.cursor = 'grab';
    
    // Initialize zoom/pan
    return new GraphZoomPan(containerId, {
        minScale: 0.3,
        maxScale: 5,
        zoomFactor: 0.1,
        ...options
    });
}

// Initialize after the graph has been rendered
let zoomPanInstance = null;
function initializeZoomPan() {
    if (!zoomPanInstance) {
        zoomPanInstance = initializeGraphZoomPan('flow-graph');
    }
}

// Schedule initialization after the graph is rendered
document.addEventListener('DOMContentLoaded', () => {
    // First attempt after 300ms
    setTimeout(initializeZoomPan, 300);
    
    // Fallback attempt after 1 second if needed
    setTimeout(() => {
        const container = document.getElementById('flow-graph');
        if (container && container.childElementCount > 1 && !zoomPanInstance) {
            initializeZoomPan();
        }
    }, 1000);
});
