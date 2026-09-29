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
  const monitorCount =
    desk.monitors_count !== undefined
      ? desk.monitors_count
      : (desk.has_monitor ? 2 : 0);

  if (monitorCount > 0) {
    const screenGeo = new THREE.BoxGeometry(0.7, 0.4, 0.02);
    const screenMat = new THREE.MeshStandardMaterial({
      color: 0x050505,
      roughness: 0.2,
    });
    const standGeo = new THREE.CylinderGeometry(0.02, 0.05, 0.25, 8);
    const standMat = new THREE.MeshStandardMaterial({ color: 0x222225, metalness: 0.7 });

    if (monitorCount === 1) {
      // 1 Monitor único centralizado
      const mStand = new THREE.Mesh(standGeo, standMat);
      mStand.position.set(0, 0.88, -0.3);
      group.add(mStand);

      const mScreen = new THREE.Mesh(screenGeo, screenMat);
      mScreen.position.set(0, 1.05, -0.3);
      mScreen.rotation.y = 0;
      group.add(mScreen);
    } else {
      // 2 ou mais Monitores (configuração estéreo angular)
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
  }

  // 3.1 Docking Station Hub (se habilitado)
  if (desk.has_docking_station) {
    const dockGeo = new THREE.BoxGeometry(0.22, 0.03, 0.14);
    const dockMat = new THREE.MeshStandardMaterial({ color: 0x1f242d, metalness: 0.8, roughness: 0.3 });
    const dockMesh = new THREE.Mesh(dockGeo, dockMat);
    dockMesh.position.set(0.65, 0.8, -0.25);
    group.add(dockMesh);
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

  // 5. Occupant: 3D Seated Figure + Floating Billboard Hologram Card
  if (desk.status === 'OCUPADA' || desk.status === 'RESERVADA') {
    const seatedOccupant = createSeatedOccupant(desk.status);
    group.add(seatedOccupant);

    const avatarSprite = createAvatarSprite(desk);
    avatarSprite.position.set(0, 1.95, 0.0);
    group.add(avatarSprite);
  }

  // Position and rotate assembly according to desk coordinates
  group.position.set(desk.pos_x, desk.pos_y, desk.pos_z);
  group.rotation.y = THREE.MathUtils.degToRad(desk.rotation_y || 0);

  return group;
}

/**
 * Creates a low-poly stylized 3D seated figure placed at the desk chair.
 */
function createSeatedOccupant(status: string): THREE.Group {
  const occupant = new THREE.Group();
  occupant.position.set(0, 0, 0.4); // placed on chair

  const isOccupied = status === 'OCUPADA';
  const shirtColor = isOccupied ? 0x5e6ad2 : 0xd97706; // indigo for occupied, amber for reserved
  const skinColor = 0xd4a373;

  const shirtMat = new THREE.MeshStandardMaterial({
    color: shirtColor,
    roughness: 0.5,
    metalness: 0.1,
  });
  const skinMat = new THREE.MeshStandardMaterial({
    color: skinColor,
    roughness: 0.6,
  });
  const pantsMat = new THREE.MeshStandardMaterial({
    color: 0x1a1b1e,
    roughness: 0.8,
  });

  // Torso
  const torsoGeo = new THREE.BoxGeometry(0.38, 0.42, 0.22);
  const torso = new THREE.Mesh(torsoGeo, shirtMat);
  torso.position.y = 0.8;
  torso.castShadow = true;
  occupant.add(torso);

  // Head
  const headGeo = new THREE.SphereGeometry(0.12, 16, 16);
  const head = new THREE.Mesh(headGeo, skinMat);
  head.position.y = 1.15;
  head.castShadow = true;
  occupant.add(head);

  // Hair
  const hairGeo = new THREE.SphereGeometry(0.125, 16, 16, 0, Math.PI * 2, 0, Math.PI / 2);
  const hairMat = new THREE.MeshStandardMaterial({ color: 0x141517, roughness: 0.9 });
  const hair = new THREE.Mesh(hairGeo, hairMat);
  hair.position.set(0, 1.16, 0);
  hair.rotation.x = -0.15;
  occupant.add(hair);

  // Arms resting towards desk
  const armGeo = new THREE.CylinderGeometry(0.045, 0.045, 0.35, 8);
  const leftArm = new THREE.Mesh(armGeo, shirtMat);
  leftArm.position.set(-0.24, 0.76, -0.06);
  leftArm.rotation.x = -Math.PI / 4;
  leftArm.rotation.z = -0.12;
  occupant.add(leftArm);

  const rightArm = new THREE.Mesh(armGeo, shirtMat);
  rightArm.position.set(0.24, 0.76, -0.06);
  rightArm.rotation.x = -Math.PI / 4;
  rightArm.rotation.z = 0.12;
  occupant.add(rightArm);

  // Upper legs horizontal on chair seat
  const upperLegGeo = new THREE.BoxGeometry(0.12, 0.1, 0.32);
  const leftLeg = new THREE.Mesh(upperLegGeo, pantsMat);
  leftLeg.position.set(-0.11, 0.53, -0.1);
  occupant.add(leftLeg);

  const rightLeg = new THREE.Mesh(upperLegGeo, pantsMat);
  rightLeg.position.set(0.11, 0.53, -0.1);
  occupant.add(rightLeg);

  // Lower legs vertical
  const lowerLegGeo = new THREE.BoxGeometry(0.1, 0.32, 0.1);
  const leftLowerLeg = new THREE.Mesh(lowerLegGeo, pantsMat);
  leftLowerLeg.position.set(-0.11, 0.32, -0.24);
  occupant.add(leftLowerLeg);

  const rightLowerLeg = new THREE.Mesh(lowerLegGeo, pantsMat);
  rightLowerLeg.position.set(0.11, 0.32, -0.24);
  occupant.add(rightLowerLeg);

  return occupant;
}

function roundRect(
  ctx: CanvasRenderingContext2D,
  x: number,
  y: number,
  w: number,
  h: number,
  r: number
) {
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.lineTo(x + w - r, y);
  ctx.quadraticCurveTo(x + w, y, x + w, y + r);
  ctx.lineTo(x + w, y + h - r);
  ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
  ctx.lineTo(x + r, y + h);
  ctx.quadraticCurveTo(x, y + h, x, y + h - r);
  ctx.lineTo(x, y + r);
  ctx.quadraticCurveTo(x, y, x + r, y);
  ctx.closePath();
}

/**
 * Creates a high-resolution billboard card showing occupant avatar/photo, name, and status.
 */
export function createAvatarSprite(desk: DeskWithOccupant): THREE.Sprite {
  const canvas = document.createElement('canvas');
  canvas.width = 512;
  canvas.height = 200;
  const ctx = canvas.getContext('2d')!;

  const texture = new THREE.CanvasTexture(canvas);
  texture.minFilter = THREE.LinearFilter;

  function renderCard(avatarImg?: HTMLImageElement) {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const isOccupied = desk.status === 'OCUPADA';
    const accentColor = isOccupied ? '#5e6ad2' : '#eab308';
    const accentBg = isOccupied ? 'rgba(94, 106, 210, 0.25)' : 'rgba(234, 179, 8, 0.25)';
    const statusText = isOccupied ? '● OCUPADA' : '● RESERVADA';

    // Rounded Box background
    ctx.save();
    ctx.fillStyle = 'rgba(12, 13, 16, 0.94)';
    ctx.strokeStyle = accentColor;
    ctx.lineWidth = 4;
    roundRect(ctx, 8, 8, 496, 184, 24);
    ctx.fill();
    ctx.stroke();
    ctx.restore();

    // Top subtle accent bar
    ctx.save();
    ctx.fillStyle = accentColor;
    roundRect(ctx, 24, 10, 464, 4, 2);
    ctx.fill();
    ctx.restore();

    // Avatar Circle (Left)
    const avatarX = 85;
    const avatarY = 100;
    const radius = 54;

    ctx.save();
    ctx.beginPath();
    ctx.arc(avatarX, avatarY, radius, 0, Math.PI * 2);
    ctx.clip();

    if (avatarImg && avatarImg.complete && avatarImg.naturalWidth > 0) {
      ctx.drawImage(avatarImg, avatarX - radius, avatarY - radius, radius * 2, radius * 2);
    } else {
      ctx.fillStyle = isOccupied ? '#353a6b' : '#6b4b12';
      ctx.fillRect(avatarX - radius, avatarY - radius, radius * 2, radius * 2);
      ctx.fillStyle = '#ffffff';
      ctx.font = 'bold 40px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      const initials = desk.occupant_name
        ? desk.occupant_name.split(' ').slice(0, 2).map((p) => p[0].toUpperCase()).join('')
        : 'U';
      ctx.fillText(initials, avatarX, avatarY);
    }
    ctx.restore();

    // Avatar border ring
    ctx.save();
    ctx.beginPath();
    ctx.arc(avatarX, avatarY, radius, 0, Math.PI * 2);
    ctx.lineWidth = 5;
    ctx.strokeStyle = accentColor;
    ctx.stroke();
    ctx.restore();

    // Text Section (Right)
    const textX = 162;

    // Baia Code
    ctx.save();
    ctx.fillStyle = '#94a3b8';
    ctx.font = 'bold 20px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
    ctx.textAlign = 'left';
    ctx.fillText(`BAIA ${desk.code}`, textX, 58);

    // Status Pill Badge
    ctx.fillStyle = accentBg;
    roundRect(ctx, 345, 38, 140, 32, 16);
    ctx.fill();
    ctx.fillStyle = accentColor;
    ctx.font = 'bold 15px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText(statusText, 415, 60);
    ctx.restore();

    // Occupant Full Name
    ctx.save();
    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 30px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
    ctx.textAlign = 'left';
    const name = desk.occupant_name || 'Colaborador';
    const displayName = name.length > 17 ? name.slice(0, 16) + '…' : name;
    ctx.fillText(displayName, textX, 106);
    ctx.restore();

    // Desk features subtitle
    ctx.save();
    ctx.fillStyle = '#64748b';
    ctx.font = '500 19px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
    ctx.textAlign = 'left';
    const featureText = desk.has_monitor ? 'Monitor Duplo • Check-in Ativo' : 'Check-in Confirmado';
    ctx.fillText(featureText, textX, 144);
    ctx.restore();

    texture.needsUpdate = true;
  }

  // Initial draw immediately
  renderCard();

  // Load avatar image if available
  const avatarUrl = desk.occupant_photo || desk.occupant_avatar;
  if (avatarUrl) {
    const img = new Image();
    img.crossOrigin = 'anonymous';
    img.onload = () => {
      renderCard(img);
    };
    img.src = avatarUrl;
  }

  const spriteMat = new THREE.SpriteMaterial({
    map: texture,
    transparent: true,
  });

  const sprite = new THREE.Sprite(spriteMat);
  sprite.scale.set(1.9, 0.75, 1.0);
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
