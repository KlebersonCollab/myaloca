import type {
  Booking,
  Desk,
  DeskWithOccupant,
  User,
  Zone,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

class ApiError extends Error {
  code: string;
  status: number;

  constructor(message: string, code: string = 'UNKNOWN_ERROR', status: number = 500) {
    super(message);
    this.name = 'ApiError';
    this.code = code;
    this.status = status;
  }
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const token = localStorage.getItem('myaloca_token');
  const headers = new Headers(options.headers || {});

  if (!headers.has('Content-Type') && !(options.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json');
  }

  if (token && !headers.has('Authorization')) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  const url = `${API_BASE_URL}${endpoint}`;
  const response = await fetch(url, { ...options, headers });

  if (!response.ok) {
    let errCode = 'HTTP_ERROR';
    let errMsg = `Request failed with status ${response.status}`;
    try {
      const errData = await response.json();
      if (errData.detail) {
        if (typeof errData.detail === 'object') {
          errCode = errData.detail.code || errCode;
          errMsg = errData.detail.message || errMsg;
        } else {
          errMsg = errData.detail;
        }
      }
    } catch {
      // not JSON
    }
    throw new ApiError(errMsg, errCode, response.status);
  }

  return response.json();
}

export const api = {
  auth: {
    async login(email: string, password: string): Promise<{ access_token: string }> {
      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);

      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData.toString(),
      });

      if (!response.ok) {
        const err = await response.json().catch(() => ({}));
        const msg = err.detail?.message || 'Falha ao autenticar usuário';
        const code = err.detail?.code || 'AUTH_ERROR';
        throw new ApiError(msg, code, response.status);
      }

      return response.json();
    },

    async getMe(): Promise<User> {
      return request<User>('/auth/me');
    },

    async register(data: Partial<User> & { password: string }): Promise<User> {
      return request<User>('/auth/register', {
        method: 'POST',
        body: JSON.stringify(data),
      });
    },
  },

  zones: {
    async list(): Promise<Zone[]> {
      return request<Zone[]>('/zones');
    },
    async create(data: { name: string; floor?: number; description?: string }): Promise<Zone> {
      return request<Zone>('/zones', {
        method: 'POST',
        body: JSON.stringify(data),
      });
    },
  },

  desks: {
    async list(zoneId?: number): Promise<Desk[]> {
      const q = zoneId ? `?zone_id=${zoneId}` : '';
      return request<Desk[]>(`/desks${q}`);
    },
    async get(id: number): Promise<Desk> {
      return request<Desk>(`/desks/${id}`);
    },
    async create(data: Partial<Desk>): Promise<Desk> {
      return request<Desk>('/desks', {
        method: 'POST',
        body: JSON.stringify(data),
      });
    },
    getQrCodeUrl(id: number): string {
      return `${API_BASE_URL}/desks/${id}/qrcode`;
    },
  },

  bookings: {
    async create(data: {
      desk_id: number;
      start_time: string;
      end_time: string;
      notes?: string;
    }): Promise<Booking> {
      return request<Booking>('/bookings', {
        method: 'POST',
        body: JSON.stringify(data),
      });
    },
    async checkIn(bookingId: number, qrCodeHash: string): Promise<Booking> {
      return request<Booking>(`/bookings/${bookingId}/checkin`, {
        method: 'POST',
        body: JSON.stringify({ qr_code_hash: qrCodeHash }),
      });
    },
    async listMy(): Promise<Booking[]> {
      return request<Booking[]>('/bookings/me');
    },
    async get3dOffice(zoneId?: number): Promise<DeskWithOccupant[]> {
      const q = zoneId ? `?zone_id=${zoneId}` : '';
      return request<DeskWithOccupant[]>(`/bookings/3d-office${q}`);
    },
  },
};
