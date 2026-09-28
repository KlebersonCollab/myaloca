import * as THREE from 'three';
import type { DeskWithOccupant } from '../types';

export const STATUS_COLORS = {
  DISPONIVEL: {
    base: 0x1a2e20,
    top: 0x27a644,
    emissive: 0x0f4019,
    hex: '#27a644',
    label: 'Disponível',
  },
  RESERVADA: {
    base: 0x3d2c0b,
    top: 0xeab308,
    emissive: 0x614805,
    hex: '#eab308',
    label: 'Reservada',
  },
  OCUPADA: {
    base: 0x201e40,
    top: 0x5e6ad2,
    emissive: 0x272c63,
    hex: '#5e6ad2',
    label: 'Ocupada',
  },
  MANUTENCAO: {
    base: 0x1f2024,
    top: 0x3e3e44,
    emissive: 0x111214,
    hex: '#3e3e44',
    label: 'Manutenção',
  },
};

/**
 * Creates a detailed 3D Desk assembly group including table, legs, dual monitors, and chair.
 */
export function createDeskGroup(desk: DeskWithOccupant): THREE.Group {
  const group = new THREE.Group();
  group.name = `desk_${desk.id}`;
  group.userData = { deskId: desk.id, desk };

  const colorConfig =
    STATUS_COLORS[desk.status as keyof typeof STATUS_COLORS] || STATUS_COLORS.DISPONIVEL;

  // 1. Table Top (Bancada)
  const topGeo = new THREE.BoxGeometry(2.0, 0.08, 1.1);
  const topMat = new THREE.MeshStandardMaterial({
    color: 0x18191c,
    roughness: 0.3,
    metalness: 0.1,
  });
  const topMesh = new THREE.Mesh(topGeo, topMat);
  topMesh.position.y = 0.75;
  topMesh.castShadow = true;
  topMesh.receiveShadow = true;
  group.add(topMesh);

  // 1.1 Colored Status Edge Strip (fita LED indicadora de status)
  const edgeGeo = new THREE.BoxGeometry(2.02, 0.04, 0.05);
  const edgeMat = new THREE.MeshStandardMaterial({
    color: colorConfig.top,
    emissive: colorConfig.emissive,
    emissiveIntensity: 0.8,
    roughness: 0.2,
  });
  const edgeMesh = new THREE.Mesh(edgeGeo, edgeMat);
  edgeMesh.position.set(0, 0.77, 0.55);
  group.add(edgeMesh);

  // 2. Metal Legs (Pernas da mesa)
  const legGeo = new THREE.CylinderGeometry(0.03, 0.03, 0.75, 12);
  const legMat = new THREE.MeshStandardMaterial({
    color: 0x2b2d33,
    metalness: 0.8,
    roughness: 0.4,
  });

  const legPositions = [
    [-0.9, 0.375, -0.45],
    [0.9, 0.375, -0.45],
    [-0.9, 0.375, 0.45],
    [0.9, 0.375, 0.45],
  ];

  legPositions.forEach(([x, y, z]) => {
    const leg = new THREE.Mesh(legGeo, legMat);
    leg.position.set(x, y, z);
    leg.castShadow = true;
    group.add(leg);
  });

  // 3. Monitor Setup (Monitores em cima da mesa)
  if (desk.has_monitor) {
    const screenGeo = new THREE.BoxGeometry(0.7, 0.4, 0.02);
    const screenMat = new THREE.MeshStandardMaterial({
      color: 0x050505,
      roughness: 0.2,
    });
    const standGeo = new THREE.CylinderGeometry(0.02, 0.05, 0.25, 8);
    const standMat = new THREE.MeshStandardMaterial({ color: 0x222225, metalness: 0.7 });

    // Monitor 1 (Esquerda)
    const m1Stand = new THREE.Mesh(standGeo, standMat);
    m1Stand.position.set(-0.35, 0.88, -0.3);
    group.add(m1Stand);

    const m1Screen = new THREE.Mesh(screenGeo, screenMat);
    m1Screen.position.set(-0.35, 1.05, -0.3);
    m1Screen.rotation.y = 0.15;
    group.add(m1Screen);

    // Monitor 2 (Direita)
    const m2Stand = new THREE.Mesh(standGeo, standMat);
    m2Stand.position.set(0.35, 0.88, -0.3);
    group.add(m2Stand);

    const m2Screen = new THREE.Mesh(screenGeo, screenMat);
    m2Screen.position.set(0.35, 1.05, -0.3);
    m2Screen.rotation.y = -0.15;
    group.add(m2Screen);
  }

  // 4. Office Chair (Cadeira ergonômica)
  const chairGroup = new THREE.Group();
  chairGroup.position.set(0, 0, 0.4);

  // Chair seat
  const seatGeo = new THREE.BoxGeometry(0.55, 0.08, 0.5);
  const chairMat = new THREE.MeshStandardMaterial({
    color: 0x121315,
    roughness: 0.7,
  });
  const seatMesh = new THREE.Mesh(seatGeo, chairMat);
  seatMesh.position.y = 0.48;
  chairGroup.add(seatMesh);

  // Chair backrest
  const backGeo = new THREE.BoxGeometry(0.5, 0.6, 0.06);
  const backMesh = new THREE.Mesh(backGeo, chairMat);
  backMesh.position.set(0, 0.8, 0.23);
  chairGroup.add(backMesh);

  // Chair stem & base
  const stemGeo = new THREE.CylinderGeometry(0.04, 0.04, 0.45, 8);
  const baseMat = new THREE.MeshStandardMaterial({ color: 0x33353a, metalness: 0.8 });
  const stemMesh = new THREE.Mesh(stemGeo, baseMat);
  stemMesh.position.y = 0.24;
  chairGroup.add(stemMesh);

  group.add(chairGroup);

  // 5. Occupant Avatar / Floating Hologram
  if (desk.status === 'OCUPADA' || desk.status === 'RESERVADA') {
    const avatarSprite = createAvatarSprite(desk);
    avatarSprite.position.set(0, 1.65, 0.0);
    group.add(avatarSprite);
  }

  // Position and rotate assembly according to desk coordinates
  group.position.set(desk.pos_x, desk.pos_y, desk.pos_z);
  group.rotation.y = THREE.MathUtils.degToRad(desk.rotation_y || 0);

  return group;
}

/**
 * Creates a circular canvas texture representing the user's avatar or initials
 */
export function createAvatarSprite(desk: DeskWithOccupant): THREE.Sprite {
  const canvas = document.createElement('canvas');
  canvas.width = 128;
  canvas.height = 128;
  const ctx = canvas.getContext('2d')!;

  // Background Circle
  ctx.beginPath();
  ctx.arc(64, 64, 58, 0, 2 * Math.PI);
  ctx.fillStyle = desk.status === 'OCUPADA' ? '#5e6ad2' : '#eab308';
  ctx.fill();
  ctx.lineWidth = 6;
  ctx.strokeStyle = '#ffffff';
  ctx.stroke();

  // Name / Initials
  const initials = desk.occupant_name
    ? desk.occupant_name
        .split(' ')
        .slice(0, 2)
        .map((p) => p[0].toUpperCase())
        .join('')
    : 'U';

  ctx.fillStyle = '#ffffff';
  ctx.font = 'bold 44px sans-serif';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText(initials, 64, 66);

  const texture = new THREE.CanvasTexture(canvas);
  texture.needsUpdate = true;

  const spriteMat = new THREE.SpriteMaterial({
    map: texture,
    transparent: true,
  });

  const sprite = new THREE.Sprite(spriteMat);
  sprite.scale.set(0.65, 0.65, 1.0);
  return sprite;
}

/**
 * Creates a subtle grid floor plane adhering to Linear Dark styling
 */
export function createOfficeFloor(width: number = 40, height: number = 40): THREE.Group {
  const floorGroup = new THREE.Group();

  // Dark matte floor
  const floorGeo = new THREE.PlaneGeometry(width, height);
  const floorMat = new THREE.MeshStandardMaterial({
    color: 0x0a0b0d,
    roughness: 0.9,
    metalness: 0.1,
  });
  const floorMesh = new THREE.Mesh(floorGeo, floorMat);
  floorMesh.rotation.x = -Math.PI / 2;
  floorMesh.receiveShadow = true;
  floorGroup.add(floorMesh);

  // Grid lines
  const gridHelper = new THREE.GridHelper(width, 40, 0x23252a, 0x141516);
  gridHelper.position.y = 0.01;
  floorGroup.add(gridHelper);

  return floorGroup;
}
