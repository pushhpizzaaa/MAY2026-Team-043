// ============================================================================
// 1. BASELINE DATA CONFIGURATIONS (FALLBACK SEEDS)
// ============================================================================

export const CATEGORIES = [
  { id: 1, name: "Women's Care", description: "Empowerment and care initiatives" },
  { id: 2, name: "Child Welfare", description: "Education and support frameworks" },
  { id: 3, name: "Elder Care & Orphanage", description: "Support for senior homes and orphanages" },
  { id: 4, name: "Environmental Plantation", description: "Tree plantation and green drives" },
  { id: 5, name: "Blood Donation", description: "Lifesaving blood donation camps" }
];

const initialUsers = [
  {
    id: "admin-sastry",
    role: "admin",
    name: "Sastry",
    email: "sastry@gmail.com",
    password: "Servants@india",
    organization: "Servants of Bharat"
  },
  {
    id: "vol-demo",
    role: "volunteer",
    name: "Arjun Kumar",
    email: "arjun@gmail.com",
    password: "password123",
    phone: "9876543210",
    bloodGroup: "O+",
    dob: "2000-05-15",
    location: "Hyderabad",
    organization: "Local College"
  }
];

const initialEvents = [
  {
    id: "evt-1",
    title: "Women's Safety & Health Awareness Clinic",
    description: "Conducting dynamic awareness drives and distributing hygiene kits.",
    category_id: 1,
    category_name: "Women's Care",
    venue: "Community Center Hall A",
    address: "Ameerpet Road",
    city: "Hyderabad",
    state: "Telangana",
    event_date: "2026-07-15",
    status: "UPCOMING"
  },
  {
    id: "evt-2",
    title: "Eco-Plantation Drive 2026",
    description: "Help us plant 500 indigenous saplings near the urban development park area.",
    category_id: 4,
    category_name: "Environmental Plantation",
    venue: "Green Belt Zone",
    address: "Phase 3, Hitech Road",
    city: "Hyderabad",
    state: "Telangana",
    event_date: "2026-07-20",
    status: "UPCOMING"
  }
];

const initialSubmissions = [
  {
    id: "sub-001",
    volunteer_id: "vol-demo",
    event_id: "evt-1",
    category_id: 1,
    image_url: "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=600",
    note: "Distributed 30 individual hygiene care packets at the Ameerpet library junction block. Active engagement recorded.",
    service_year: 2026,
    quarter: 3,
    status: "PENDING",
    submitted_at: "2026-07-01"
  },
  {
    id: "sub-002",
    volunteer_id: "vol-demo",
    event_id: "evt-2",
    category_id: 4,
    image_url: "https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?w=600",
    note: "Successfully dug pits and planted 5 neem saplings along the designated zone line. Tagged pictures attached.",
    service_year: 2026,
    quarter: 3,
    status: "PENDING",
    submitted_at: "2026-07-03"
  },
  {
    id: "sub-003",
    volunteer_id: "vol-external-user",
    event_id: null,
    category_id: 5,
    image_url: "https://images.unsplash.com/photo-1615461066841-6116ecdacd6f?w=600",
    note: "Independent Operation: Donated 1 unit of O+ blood at the district civil hospital ward due to emergency alert request.",
    service_year: 2026,
    quarter: 3,
    status: "PENDING",
    submitted_at: "2026-07-06"
  },
  {
    id: "sub-004",
    volunteer_id: "vol-demo",
    event_id: null,
    category_id: 3,
    image_url: "https://images.unsplash.com/photo-1516627145497-ae6968895b74?w=600",
    note: "Archived Record: Conducted voluntary weekend storytelling reading block session at the local elder care complex.",
    service_year: 2026,
    quarter: 2,
    status: "APPROVED",
    submitted_at: "2026-05-18"
  }
];

// ============================================================================
// 2. STORAGE ENGINE METHODS & REACTIVE INITIALIZATION
// ============================================================================

/**
 * Safely fetches dataset from local storage or populates it with fallbacks if empty.
 * @param {string} key 
 * @param {Array|Object} fallback 
 * @returns {Array|Object} Parsed JSON data layer
 */
export const getLocalStorageData = (key, fallback) => {
  const data = localStorage.getItem(key);
  if (!data) {
    localStorage.setItem(key, JSON.stringify(fallback));
    return fallback;
  }
  return JSON.parse(data);
};

/**
 * Syncs runtime memory mutations back directly to state persistence block.
 * @param {string} key 
 * @param {Array|Object} data 
 */
export const saveLocalStorageData = (key, data) => {
  localStorage.setItem(key, JSON.stringify(data));
};

// Seed baseline records on script execution cycle
export const initializedUsers = getLocalStorageData('sob_users', initialUsers);
export const initializedEvents = getLocalStorageData('sob_events', initialEvents);
export const initializedSubmissions = getLocalStorageData('sob_submissions', initialSubmissions);