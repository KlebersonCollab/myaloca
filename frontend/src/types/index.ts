export type UserRole = 'admin' | 'gestor' | 'colaborador';

export interface User {
  id: number;
  email: string;
  full_name: string;
  role: UserRole;
  avatar_url?: string | null;
  photo_url?: string | null;
  job_title?: string | null;
  department?: string | null;
  is_active: boolean;
  created_at: string;
}

export interface Zone {
  id: number;
  name: string;
  floor: number;
  description?: string | null;
  is_active: boolean;
  created_at: string;
}

export type DeskStatus = 'DISPONIVEL' | 'RESERVADA' | 'OCUPADA' | 'MANUTENCAO';

export interface Desk {
  id: number;
  code: string;
  zone_id: number;
  pos_x: number;
  pos_y: number;
  pos_z: number;
  rotation_y: number;
  has_monitor: boolean;
  has_docking_station: boolean;
  is_standing_desk: boolean;
  status: DeskStatus;
  qr_code_hash: string;
  created_at: string;
}

export interface DeskWithOccupant extends Desk {
  occupant_name?: string | null;
  occupant_avatar?: string | null;
  occupant_photo?: string | null;
  booking_id?: number | null;
}

export type BookingStatus =
  | 'PENDENTE_CHECKIN'
  | 'CHECKED_IN'
  | 'CANCELADA_USUARIO'
  | 'EXPIRADA_NO_SHOW'
  | 'FINALIZADA';

export interface Booking {
  id: number;
  desk_id: number;
  user_id: number;
  start_time: string;
  end_time: string;
  checkin_deadline: string;
  checked_in_at?: string | null;
  status: BookingStatus;
  notes?: string | null;
  created_at: string;
}
