import * as THREE from 'three';
import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/examples/jsm/postprocessing/UnrealBloomPass.js';

// ==============================
// Audio + MIDI Playback Manager
// ==============================
let currentMidi = null;
let synth = null;
const statusElement = document.getElementById('status');

// Update status display
function updateStatus(message) {
  statusElement.textContent = `Status: ${message}`;
  console.log(message);
}

// Initialize when the page loads
window.addEventListener('load', async () => {
  // Initialize Tone.js
  await Tone.start();
  
  // Create a polyphonic synth with increased polyphony and optimized settings
  synth = new Tone.PolySynth(Tone.Synth, {
    maxPolyphony: 64,
    voice: {
      oscillator: {
        type: "sine"
      },
      envelope: {
        attack: 0.02,
        decay: 0.1,
        sustain: 0.3,
        release: 1
      }
    }
  }).toDestination();
  
  // Reduce the overall volume to prevent clipping
  synth.volume.value = -12;
  
  updateStatus('Ready to play MIDI files');
});

// We'll call this after loading a MIDI file
async function initMidiPlayer(arrayBuffer) {
  try {
    // Parse MIDI file
    const midi = new Midi(arrayBuffer);
    currentMidi = midi;
    
    // Enable the play/pause buttons
    document.getElementById('play-btn').disabled = false;
    document.getElementById('pause-btn').disabled = false;
    
    updateStatus('MIDI file loaded successfully');
    console.log('MIDI file loaded:', midi);
    
    return Promise.resolve();
  } catch (error) {
    console.error('Error loading MIDI file:', error);
    updateStatus('Error loading MIDI file');
    return Promise.reject(error);
  }
}

// ===============
// Drag & Drop
// ===============
const dropZone = document.getElementById('drop-zone');
dropZone.addEventListener('dragover', (e) => {
  e.preventDefault();
  dropZone.classList.add('hover');
});
dropZone.addEventListener('dragleave', () => {
  dropZone.classList.remove('hover');
});
dropZone.addEventListener('drop', async (e) => {
  e.preventDefault();
  dropZone.classList.remove('hover');

  if (e.dataTransfer.files.length > 0) {
    const file = e.dataTransfer.files[0];
    // Basic check for .mid file extension
    if (file.name.endsWith('.mid') || file.type === 'audio/midi') {
      updateStatus('Loading MIDI file...');
      const reader = new FileReader();
      reader.onload = async () => {
        try {
          await initMidiPlayer(reader.result);
        } catch (error) {
          console.error('Failed to initialize MIDI player:', error);
          alert('Error loading MIDI file. Please check console for details.');
        }
      };
      reader.onerror = (error) => {
        console.error('Error reading file:', error);
        updateStatus('Error reading MIDI file');
        alert('Error reading MIDI file');
      };
      reader.readAsArrayBuffer(file);
    } else {
      alert('Please drop a valid MIDI (.mid) file.');
    }
  }
});

// ===============
// Play/Pause
// ===============
const playBtn = document.getElementById('play-btn');
const pauseBtn = document.getElementById('pause-btn');

let isPlaying = false;
let currentNotes = new Map();
let startTime;
let lastScheduledTime = 0;

function scheduleNotes() {
  if (!currentMidi || !isPlaying) return;
  
  const now = Tone.now();
  if (!startTime) startTime = now;
  
  const lookAheadTime = 0.1; // Schedule 100ms ahead
  const scheduleWindow = now + lookAheadTime;
  
  // Only schedule notes that haven't been scheduled yet
  currentMidi.tracks.forEach(track => {
    track.notes.forEach(note => {
      const noteStartTime = startTime + note.time;
      
      if (noteStartTime >= now && 
          noteStartTime < scheduleWindow && 
          noteStartTime > lastScheduledTime) {
        
        // Schedule note to play
        synth.triggerAttackRelease(
          note.name,
          note.duration,
          noteStartTime,
          note.velocity * 0.7
        );
        
        // Trigger visualization with instrument information
        spawnVisualForNote(
          note.midi, 
          note.velocity * 127,
          track.instrument?.number || 0  // Pass instrument number instead of channel
        );
      }
    });
  });
  
  lastScheduledTime = scheduleWindow;
  requestAnimationFrame(scheduleNotes);
}

playBtn.addEventListener('click', async () => {
  if (currentMidi && !isPlaying) {
    await Tone.start();
    
    // Reset scheduling state
    isPlaying = true;
    startTime = Tone.now();
    lastScheduledTime = 0;
    
    // Start transport and scheduling
    Tone.Transport.start();
    scheduleNotes();
    updateStatus('Playing MIDI file');
  }
});

pauseBtn.addEventListener('click', () => {
  isPlaying = false;
  startTime = null;
  lastScheduledTime = 0;
  synth.releaseAll();
  Tone.Transport.stop();
  updateStatus('Playback paused');
});

// Clean up when leaving the page
window.addEventListener('beforeunload', () => {
  isPlaying = false;
  if (synth) {
    synth.releaseAll();
    synth.dispose();
  }
  Tone.Transport.stop();
});

// ======================
// Three.js Visualization
// ======================
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(
  75,
  window.innerWidth / window.innerHeight,
  0.1,
  1000
);
camera.position.z = 50;

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

// Add post-processing for glow effects
const composer = new EffectComposer(renderer);
const renderPass = new RenderPass(scene, camera);
composer.addPass(renderPass);

const bloomPass = new UnrealBloomPass(
  new THREE.Vector2(window.innerWidth, window.innerHeight),
  1.5, // bloom intensity
  0.4, // bloom radius
  0.85 // bloom threshold
);
composer.addPass(bloomPass);

// Create a reactive sphere (invisible) that will serve as the base for the grid of nodes
const sphereGeometry = new THREE.SphereGeometry(24, 32, 32); // Decreased from 30 to 24
const sphereMaterial = new THREE.MeshPhongMaterial({
  color: 0x000000,    // Black
  emissive: 0x000000,
  shininess: 50,
  transparent: true,
  opacity: 0.0,       // Fully transparent so the sphere itself is invisible
  depthWrite: false   // Prevent sphere from occluding grid nodes
});
const reactiveSphere = new THREE.Mesh(sphereGeometry, sphereMaterial);
scene.add(reactiveSphere);

// Add a white wireframe overlay to the sphere for visibility
const wireframeMaterial = new THREE.MeshBasicMaterial({
  color: 0xffffff,
  wireframe: true,
  transparent: true,
  opacity: 0.5
});
const sphereWireframe = new THREE.Mesh(sphereGeometry, wireframeMaterial);
reactiveSphere.add(sphereWireframe);

// --- Create a grid of nodes on the sphere surface ---
let gridNodes = [];
const numPitchClasses = 12; // one ring for each pitch class (C, C#, D, etc.)
const nodesPerRing = 24;    // number of nodes in each ring
const gridRadius = 24;      // sphere radius

// Create rings of nodes, one ring per pitch class
for (let pitchClass = 0; pitchClass < numPitchClasses; pitchClass++) {
  // Calculate the height of this ring on the sphere
  // Map pitch classes from bottom to top of sphere
  const phi = ((pitchClass + 1) / (numPitchClasses + 1)) * Math.PI;
  
  // Create nodes around this ring
  for (let j = 0; j < nodesPerRing; j++) {
    const theta = (j / nodesPerRing) * 2 * Math.PI; // position around the ring
    
    // Convert spherical coordinates to Cartesian
    const x = gridRadius * Math.sin(phi) * Math.cos(theta);
    const y = gridRadius * Math.cos(phi);
    const z = gridRadius * Math.sin(phi) * Math.sin(theta);
    
    // Create a small node (a little sphere)
    const nodeGeometry = new THREE.SphereGeometry(0.3, 8, 8);
    const nodeMaterial = new THREE.MeshPhongMaterial({
      color: 0x000000,
      emissive: 0x000000,
      shininess: 50
    });
    const node = new THREE.Mesh(nodeGeometry, nodeMaterial);
    node.position.set(x, y, z);
    
    // Store the pitch class with the node for reference
    node.userData = { pitchClass };
    
    // Add the node as a child of the reactive sphere so it rotates with it
    reactiveSphere.add(node);
    gridNodes.push(node);
  }
}

// Global arrays for visual effects
let ripples = [];
let particleBursts = [];

/**
 * Creates a ripple effect at the given world position.
 * @param {THREE.Vector3} position - World position where the ripple should appear.
 * @param {THREE.Color} color - Color of the ripple.
 */
function createRipple(position, color) {
  const rippleGeometry = new THREE.RingGeometry(0.5, 0.6, 32);
  const rippleMaterial = new THREE.MeshBasicMaterial({
    color: color,
    transparent: true,
    opacity: 1,
    side: THREE.DoubleSide,
    blending: THREE.AdditiveBlending,
    depthWrite: false
  });
  const ripple = new THREE.Mesh(rippleGeometry, rippleMaterial);
  ripple.position.copy(position);
  ripple.lookAt(camera.position); // Make ripple face the camera
  scene.add(ripple);
  ripples.push({ mesh: ripple, startTime: time });
}

/**
 * Creates a particle burst effect at the given world position.
 * @param {THREE.Vector3} position - The origin position for the burst.
 * @param {THREE.Color} color - The base color for the particles.
 */
function createParticleBurst(position, color) {
  const numParticles = 20;
  const particles = [];
  const particleGeometry = new THREE.SphereGeometry(0.1, 8, 8);
  for (let i = 0; i < numParticles; i++) {
    const particleMaterial = new THREE.MeshBasicMaterial({
      color: color,
      transparent: true,
      opacity: 1,
      blending: THREE.AdditiveBlending,
      depthWrite: false
    });
    const particle = new THREE.Mesh(particleGeometry, particleMaterial);
    particle.position.copy(position);
    // Assign a random velocity vector
    const velocity = new THREE.Vector3(
      (Math.random() - 0.5) * 0.2,
      (Math.random() - 0.5) * 0.2,
      (Math.random() - 0.5) * 0.2
    );
    particles.push({ particle, velocity, startTime: time });
    scene.add(particle);
  }
  particleBursts.push(particles);
}

/**
 * Updates grid nodes in response to a MIDI note.
 * @param {number} note - MIDI note number (0-127)
 * @param {number} velocity - Note velocity (0-127)
 * @param {number} [instrument=0] - MIDI program number (0-127)
 */
function spawnVisualForNote(note, velocity, instrument = 0) {
  const normalizedVelocity = velocity / 127;
  
  // Calculate pitch class (0-11) and octave
  const pitchClass = note % 12;
  const octave = Math.floor(note / 12);
  
  // Define colors for different instrument families
  const instrumentColors = {
    piano: { h: 0.6, s: 0.3, l: 0.7 },
    chromaticPercussion: { h: 0.15, s: 0.8, l: 0.6 },
    organ: { h: 0.75, s: 0.7, l: 0.5 },
    guitar: { h: 0.3, s: 0.8, l: 0.5 },
    bass: { h: 0.6, s: 0.8, l: 0.4 },
    strings: { h: 0.0, s: 0.8, l: 0.5 },
    ensemble: { h: 0.08, s: 0.8, l: 0.5 },
    brass: { h: 0.12, s: 0.8, l: 0.5 },
    reed: { h: 0.85, s: 0.8, l: 0.5 },
    pipe: { h: 0.5, s: 0.8, l: 0.5 },
    synthLead: { h: 0.6, s: 0.9, l: 0.6 },
    synthPad: { h: 0.7, s: 0.6, l: 0.5 },
    synthFx: { h: 0.3, s: 0.9, l: 0.6 },
    ethnic: { h: 0.08, s: 0.7, l: 0.4 },
    percussive: { h: 0.15, s: 0.9, l: 0.5 },
    soundEffects: { h: 0.0, s: 0.0, l: 0.7 }
  };

  let color;
  if (instrument <= 7) color = instrumentColors.piano;
  else if (instrument <= 15) color = instrumentColors.chromaticPercussion;
  else if (instrument <= 23) color = instrumentColors.organ;
  else if (instrument <= 31) color = instrumentColors.guitar;
  else if (instrument <= 39) color = instrumentColors.bass;
  else if (instrument <= 47) color = instrumentColors.strings;
  else if (instrument <= 55) color = instrumentColors.ensemble;
  else if (instrument <= 63) color = instrumentColors.brass;
  else if (instrument <= 71) color = instrumentColors.reed;
  else if (instrument <= 79) color = instrumentColors.pipe;
  else if (instrument <= 87) color = instrumentColors.synthLead;
  else if (instrument <= 95) color = instrumentColors.synthPad;
  else if (instrument <= 103) color = instrumentColors.synthFx;
  else if (instrument <= 111) color = instrumentColors.ethnic;
  else if (instrument <= 119) color = instrumentColors.percussive;
  else color = instrumentColors.soundEffects;

  const brightColor = new THREE.Color().setHSL(color.h, color.s, color.l);
  brightColor.r = Math.min(1.0, brightColor.r * 1.5);
  brightColor.g = Math.min(1.0, brightColor.g * 1.5);
  brightColor.b = Math.min(1.0, brightColor.b * 1.5);
  
  const matchingNodes = gridNodes.filter(node => node.userData.pitchClass === pitchClass);
  const startIndex = Math.floor((octave / 8) * nodesPerRing);
  const numNodesToLight = Math.max(1, Math.floor(normalizedVelocity * 3));
  
  for (let i = 0; i < numNodesToLight; i++) {
    const nodeIndex = (startIndex + i) % nodesPerRing;
    const node = matchingNodes[nodeIndex];
    if (node) {
      node.material.emissive.copy(brightColor);
      const scaleFactor = 2.5 + normalizedVelocity * 1.0;
      node.scale.set(scaleFactor, scaleFactor, scaleFactor);
      
      const worldPos = new THREE.Vector3();
      node.getWorldPosition(worldPos);
      createRipple(worldPos, brightColor);
      createParticleBurst(worldPos, brightColor);
    }
  }
}

// Animation loop
let time = 0;
const center = new THREE.Vector3(0, 0, 0);

function animate() {
  requestAnimationFrame(animate);
  time += 0.001;
  
  reactiveSphere.rotation.x += 0.005;
  reactiveSphere.rotation.y += 0.005;
  
  gridNodes.forEach((node) => {
    node.material.emissive.lerp(new THREE.Color(0x000000), 0.02);
    node.scale.lerp(new THREE.Vector3(1, 1, 1), 0.02);
  });
  
  // Update ripple effects
  for (let i = ripples.length - 1; i >= 0; i--) {
    const rippleObj = ripples[i];
    const age = time - rippleObj.startTime;
    const newScale = 1 + age * 5;
    rippleObj.mesh.scale.set(newScale, newScale, newScale);
    rippleObj.mesh.material.opacity = Math.max(0, 1 - age * 2);
    rippleObj.mesh.lookAt(camera.position);
    if (rippleObj.mesh.material.opacity <= 0.01) {
      scene.remove(rippleObj.mesh);
      rippleObj.mesh.geometry.dispose();
      rippleObj.mesh.material.dispose();
      ripples.splice(i, 1);
    }
  }
  
  // Update particle burst effects
  for (let b = particleBursts.length - 1; b >= 0; b--) {
    const burst = particleBursts[b];
    for (let i = burst.length - 1; i >= 0; i--) {
      const pObj = burst[i];
      const age = time - pObj.startTime;
      pObj.particle.position.add(pObj.velocity);
      pObj.particle.material.opacity = Math.max(0, 1 - age * 3);
      if (pObj.particle.material.opacity <= 0.01) {
        scene.remove(pObj.particle);
        pObj.particle.geometry.dispose();
        pObj.particle.material.dispose();
        burst.splice(i, 1);
      }
    }
    if (burst.length === 0) {
      particleBursts.splice(b, 1);
    }
  }
  
  camera.position.x = Math.sin(time * 0.2) * 50;
  camera.position.z = Math.cos(time * 0.2) * 50;
  camera.lookAt(center);
  
  // Make reactive sphere pulsate subtly
  const pulsate = 1 + Math.sin(time * 5) * 0.03;
  reactiveSphere.scale.set(pulsate, pulsate, pulsate);
  
  // Modulate ambient light intensity for added dynamism
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.5 + 0.2 * Math.sin(time * 0.5));
  ambientLight.intensity = 0.5 + 0.2 * Math.sin(time * 0.5);
  
  composer.render();
}

// Start the animation loop
animate();

// Handle window resizing
window.addEventListener('resize', () => {
  const width = window.innerWidth;
  const height = window.innerHeight;
  
  camera.aspect = width / height;
  camera.updateProjectionMatrix();
  
  renderer.setSize(width, height);
  composer.setSize(width, height);
});
