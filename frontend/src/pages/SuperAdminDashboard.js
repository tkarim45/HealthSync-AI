import { useState, useEffect } from "react";
import axios from "axios";
import { useAuth } from "../context/AuthContext";
import { motion } from "framer-motion";
import NavBar from "../components/layout/NavBar";
import { FaHospital, FaUserShield, FaUserMd, FaBuilding, FaCalendar, FaHeart, FaUserPlus, FaEdit, FaTrash } from "react-icons/fa";

// Footer Component
const Footer = () => {
  const footerVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.6, ease: "easeOut" } },
  };

  return (
    <motion.footer className="bg-gray-50 py-6 border-t border-gray-200" initial="hidden" animate="visible" variants={footerVariants}>
      <div className="max-w-7xl mx-auto px-4 flex flex-col md:flex-row justify-between items-center text-gray-600">
        <p className="text-sm">© {new Date().getFullYear()} HealthSync AI. All rights reserved.</p>
        <div className="flex items-center space-x-2 mt-2 md:mt-0">
          <span className="text-sm">Made with</span>
          <motion.span className="text-teal-500" animate={{ scale: [1, 1.2, 1] }} transition={{ duration: 1.5, repeat: Infinity, ease: "easeInOut" }}>
            <FaHeart />
          </motion.span>
          <span className="text-sm">by the HealthSync Team</span>
        </div>
      </div>
    </motion.footer>
  );
};

// Dynamic Content Component
const SuperAdminContent = ({
  activeSection,
  hospitals,
  admins,
  doctors,
  departments,
  appointments,
  hospitalForm,
  setHospitalForm,
  adminForm,
  setAdminForm,
  createAdminForm,
  setCreateAdminForm,
  editHospitalForm,
  setEditHospitalForm,
  handleHospitalSubmit,
  handleAdminSubmit,
  handleCreateAdminSubmit,
  handleUpdateHospital,
  handleDeleteHospital,
  handleDeleteAdmin,
  handleDeleteDoctor,
  hospitalMessage,
  hospitalError,
  adminMessage,
  adminError,
  createAdminMessage,
  createAdminError,
  updateHospitalMessage,
  updateHospitalError,
  deleteHospitalMessage,
  deleteHospitalError,
  deleteAdminMessage,
  deleteAdminError,
  deleteDoctorMessage,
  deleteDoctorError,
  setActiveSection,
  isLoading, // New prop for loading state
}) => {
  const contentVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.5 } },
  };

  const renderContent = () => {
    switch (activeSection) {
      case "welcome":
        return (
          <motion.div variants={contentVariants} initial="hidden" animate="visible">
            <p className="text-gray-600">Welcome to the Super Admin Dashboard. Use the cards above to manage hospitals, admins, doctors, departments, and appointments.</p>
          </motion.div>
        );
      case "hospitals":
        return (
          <motion.div variants={contentVariants} initial="hidden" animate="visible" className="bg-white p-6 rounded-lg shadow-lg border border-gray-200">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">Hospitals</h2>
            {hospitals.length === 0 ? (
              <p className="text-gray-600">No hospitals available.</p>
            ) : (
              <table className="w-full text-left">
                <thead>
                  <tr className="border-b">
                    <th className="py-2 px-4 text-gray-700 font-semibold">Name</th>
                    <th className="py-2 px-4 text-gray-700 font-semibold">Address</th>
                    <th className="py-2 px-4 text-gray-700 font-semibold">Latitude</th>
                    <th className="py-2 px-4 text-gray-700 font-semibold">Longitude</th>
                    <th className="py-2 px-4 text-gray-700 font-semibold">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {hospitals.map((hospital) => (
                    <tr key={hospital.id} className="border-b">
                      <td className="py-2 px-4">{hospital.name}</td>
                      <td className="py-2 px-4">{hospital.address}</td>
                      <td className="py-2 px-4">{hospital.lat}</td>
                      <td className="py-2 px-4">{hospital.lng}</td>
                      <td className="py-2 px-4 flex space-x-2">
                        <button
                          onClick={() => {
                            setEditHospitalForm({
                              id: hospital.id,
                              name: hospital.name,
                              address: hospital.address,
                              lat: hospital.lat,
                              lng: hospital.lng,
                            });
                            setActiveSection("edit-hospital");
                          }}
                          className="text-teal-500 hover:text-teal-600"
                          title="Edit"
                          disabled={isLoading}
                        >
                          <FaEdit />
                        </button>
                        <button onClick={() => handleDeleteHospital(hospital.id)} className="text-red-500 hover:text-red-600" title="Delete" disabled={isLoading}>
                          <FaTrash />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
            {deleteHospitalMessage && <p className="text-green-500 text-sm mt-4">{deleteHospitalMessage}</p>}
            {deleteHospitalError && <p className="text-red-500 text-sm mt-4">{deleteHospitalError}</p>}
          </motion.div>
        );
      case "add-hospital":
        return (
          <motion.div variants={contentVariants} initial="hidden" animate="visible" className="bg-white p-6 rounded-lg shadow-lg border border-gray-200">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">Add Hospital</h2>
            {admins.length === 0 ? (
              <p className="text-red-500 text-sm mb-4">No admins available. Create an admin first to add a hospital.</p>
            ) : (
              <form onSubmit={handleHospitalSubmit}>
                <div className="space-y-4">
                  <div>
                    <label className="block text-gray-700 text-sm font-semibold mb-2">Hospital Name</label>
                    <input type="text" value={hospitalForm.name} onChange={(e) => setHospitalForm({ ...hospitalForm, name: e.target.value })} className="w-full p-3 rounded-lg border border-gray-300 focus:outline-none focus:border-teal-500" placeholder="e.g., City Hospital" required disabled={admins.length === 0 || isLoading} />
                  </div>
                  <div>
                    <label className="block text-gray-700 text-sm font-semibold mb-2">Address</label>
                    <input type="text" value={hospitalForm.address} onChange={(e) => setHospitalForm({ ...hospitalForm, address: e.target.value })} className="w-full p-3 rounded-lg border border-gray-300 focus:outline-none focus:border-teal-500" placeholder="e.g., 123 Main St" required disabled={admins.length === 0 || isLoading} />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-gray-700 text-sm font-semibold mb-2">Latitude</label>
                      <input type="number" step="any" value={hospitalForm.lat} onChange={(e) => setHospitalForm({ ...hospitalForm, lat: e.target.value })} className="w-full p-3 rounded-lg border border-gray-300 focus:outline-none focus:border-teal-500" placeholder="e.g., 40.7128" required disabled={admins.length === 0 || isLoading} />
                    </div>
                    <div>
                      <label className="block text-gray-700 text-sm font-semibold mb-2">Longitude</label>
                      <input type="number" step="any" value={hospitalForm.lng} onChange={(e) => setHospitalForm({ ...hospitalForm, lng: e.target.value })} className="w-full p-3 rounded-lg border border-gray-300 focus:outline-none focus:border-teal-500" placeholder="e.g., -74.0060" required disabled={admins.length === 0 || isLoading} />
                    </div>
                  </div>
                </div>
                {hospitalMessage && <p className="text-green-500 text-sm mt-4">{hospitalMessage}</p>}
                {hospitalError && <p className="text-red-500 text-sm mt-4">{hospitalError}</p>}
                <button type="submit" className="mt-6 w-full p-3 bg-teal-500 text-white rounded-lg font-semibold hover:bg-teal-600 disabled:bg-gray-400" disabled={admins.length === 0 || isLoading}>
                  {isLoading ? "Adding..." : "Add Hospital"}
                </button>
              </form>
            )}
          </motion.div>
        );
      case "edit-hospital":
        return (
          <motion.div variants={contentVariants} initial="hidden" animate="visible" className="bg-white p-6 rounded-lg shadow-lg border border-gray-200">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">Edit Hospital</h2>
            <form onSubmit={(e) => handleUpdateHospital(e, editHospitalForm.id)}>
              <div className="space-y-4">
                <div>
                  <label className="block text-gray-700 text-sm font-semibold mb-2">Hospital Name</label>
                  <input type="text" value={editHospitalForm.name} onChange={(e) => setEditHospitalForm({ ...editHospitalForm, name: e.target.value })} className="w-full p-3 rounded-lg border border-gray-300 focus:outline-none focus:border-teal-500" placeholder="e.g., City Hospital" required disabled={isLoading} />
                </div>
                <div>
                  <label className="block text-gray-700 text-sm font-semibold mb-2">Address</label>
                  <input type="text" value={editHospitalForm.address} onChange={(e) => setEditHospitalForm({ ...editHospitalForm, address: e.target.value })} className="w-full p-3 rounded-lg border border-gray-300 focus:outline-none focus:border-teal-500" placeholder="e.g., 123 Main St" required disabled={isLoading} />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-gray-700 text-sm font-semibold mb-2">Latitude</label>
                    <input type="number" step="any" value={editHospitalForm.lat} onChange={(e) => setEditHospitalForm({ ...editHospitalForm, lat: e.target.value })} className="w-full p-3 rounded-lg border border-gray-300 focus:outline-none focus:border-teal-500" placeholder="e.g., 40.7128" required disabled={isLoading} />
                  </div>
                  <div>
                    <label className="block text-gray-700 text-sm font-semibold mb-2">Longitude</label>
                    <input type="number" step="any" value={editHospitalForm.lng} onChange={(e) => setEditHospitalForm({ ...editHospitalForm, lng: e.target.value })} className="w-full p-3 rounded-lg border border-gray-300 focus:outline-none focus:border-teal-500" placeholder="e.g., -74.0060" required disabled={isLoading} />
                  </div>
                </div>
              </div>
              {updateHospitalMessage && <p className="text-green-500 text-sm mt-4">{updateHospitalMessage}</p>}
              {updateHospitalError && <p className="text-red-500 text-sm mt-4">{updateHospitalError}</p>}
              <div className="flex space-x-4 mt-6">
                <button type="submit" className="w-full p-3 bg-teal-500 text-white rounded-lg font-semibold hover:bg-teal-600 disabled:bg-gray-400" disabled={isLoading}>
                  {isLoading ? "Updating..." : "Update Hospital"}
                </button>
                <button type="button" onClick={() => setActiveSection("hospitals")} className="w-full p-3 bg-gray-500 text-white rounded-lg font-semibold hover:bg-gray-600 disabled:bg-gray-400" disabled={isLoading}>
                  Cancel
                </button>
              </div>
            </form>
          </motion.div>
        );
      case "admins":
        return (
          <motion.div variants={contentVariants} initial="hidden" animate="visible" className="bg-white p-6 rounded-lg shadow-lg border border-gray-200">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">Admins</h2>
            {admins.length === 0 ? (
              <p className="text-gray-600">No admins available.</p>
            ) : (
              <table className="w-full text-left">
                <thead>
                  <tr className="border-b">
                    <th className="py-2 px-4 text-gray-700 font-semibold">Username</th>
                    <th className="py-2 px-4 text-gray-700 font-semibold">Email</th>
                    <th className="py-2 px-4 text-gray-700 font-semibold">Role</th>
                    <th className="py-2 px-4 text-gray-700 font-semibold">Hospital</th>
                    <th className="py-2 px-4 text-gray-700 font-semibold">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {admins.map((admin) => (
                    <tr key={admin.id} className="border-b">
                      <td className="py-2 px-4">{admin.username}</td>
                      <td className="py-2 px-4">{admin.email}</td>
                      <td className="py-2 px-4">{admin.role}</td>
                      <td className="py-2 px-4">{admin.hospital_name || "None"}</td>
                      <td className="py-2 px-4">
                        <button onClick={() => handleDeleteAdmin(admin.id)} className="text-red-500 hover:text-red-600" title="Delete" disabled={isLoading}>
                          <FaTrash />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
            {deleteAdminMessage && <p className="text-green-500 text-sm mt-4">{deleteAdminMessage}</p>}
            {deleteAdminError && <p className="text-red-500 text-sm mt-4">{deleteAdminError}</p>}
          </motion.div>
        );
      case "assign-admin":
        return (
          <motion.div variants={contentVariants} initial="hidden" animate="visible" className="bg-white p-6 rounded-lg shadow-lg border border-gray-200">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">Assign Admin to Hospital</h2>
            {admins.length === 0 ? (
              <p className="text-red-500 text-sm mb-4">No admins available. Create an admin first.</p>
            ) : (
              <form onSubmit={handleAdminSubmit}>
                <div className="space-y-4">
                  <div>
                    <label className="block text-gray-700 text-sm font-semibold mb-2">Hospital</label>
                    <select value={adminForm.hospital_id} onChange={(e) => setAdminForm({ ...adminForm, hospital_id: e.target.value })} className="w-full p-3 rounded-lg border border-gray-300 focus:outline-none focus:border-teal-500" required disabled={isLoading}>
                      <option value="">Select Hospital</option>
                      {hospitals.map((hospital) => (
                        <option key={hospital.id} value={hospital.id}>
                          {hospital.name}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-gray-700 text-sm font-semibold mb-2">Admin</label>
                    <select value={adminForm.admin_id} onChange={(e) => setAdminForm({ ...adminForm, admin_id: e.target.value })} className="w-full p-3 rounded-lg border border-gray-300 focus:outline-none focus:border-teal-500" required disabled={isLoading}>
                      <option value="">Select Admin</option>
                      {admins.map((admin) => (
                        <option key={admin.id} value={admin.id}>
                          {admin.username}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
                {adminMessage && <p className="text-green-500 text-sm mt-4">{adminMessage}</p>}
                {adminError && <p className="text-red-500 text-sm mt-4">{adminError}</p>}
                <button type="submit" className="mt-6 w-full p-3 bg-teal-500 text-white rounded-lg font-semibold hover:bg-teal-600 disabled:bg-gray-400" disabled={admins.length === 0 || isLoading}>
                  {isLoading ? "Assigning..." : "Assign Admin"}
                </button>
              </form>
            )}
          </motion.div>
        );
      case "create-admin":
        return (
          <motion.div variants={contentVariants} initial="hidden" animate="visible" className="bg-white p-6 rounded-lg shadow-lg border border-gray-200">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">Create Admin</h2>
            <form onSubmit={handleCreateAdminSubmit}>
              <div className="space-y-4">
                <div>
                  <label className="block text-gray-700 text-sm font-semibold mb-2">Username</label>
                  <input type="text" value={createAdminForm.username} onChange={(e) => setCreateAdminForm({ ...createAdminForm, username: e.target.value })} className="w-full p-3 rounded-lg border border-gray-300 focus:outline-none focus:border-teal-500" placeholder="e.g., admin1" required disabled={isLoading} />
                </div>
                <div>
                  <label className="block text-gray-700 text-sm font-semibold mb-2">Email</label>
                  <input type="email" value={createAdminForm.email} onChange={(e) => setCreateAdminForm({ ...createAdminForm, email: e.target.value })} className="w-full p-3 rounded-lg border border-gray-300 focus:outline-none focus:border-teal-500" placeholder="e.g., admin1@example.com" required disabled={isLoading} />
                </div>
                <div>
                  <label className="block text-gray-700 text-sm font-semibold mb-2">Password</label>
                  <input type="password" value={createAdminForm.password} onChange={(e) => setCreateAdminForm({ ...createAdminForm, password: e.target.value })} className="w-full p-3 rounded-lg border border-gray-300 focus:outline-none focus:border-teal-500" placeholder="Enter password" required disabled={isLoading} />
                </div>
                <div>
                  <label className="block text-gray-700 text-sm font-semibold mb-2">Assign to Hospital (Optional)</label>
                  <select value={createAdminForm.hospital_id} onChange={(e) => setCreateAdminForm({ ...createAdminForm, hospital_id: e.target.value })} className="w-full p-3 rounded-lg border border-gray-300 focus:outline-none focus:border-teal-500" disabled={isLoading}>
                    <option value="">No Hospital</option>
                    {hospitals.map((hospital) => (
                      <option key={hospital.id} value={hospital.id}>
                        {hospital.name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
              {createAdminMessage && <p className="text-green-500 text-sm mt-4">{createAdminMessage}</p>}
              {createAdminError && <p className="text-red-500 text-sm mt-4">{createAdminError}</p>}
              <button type="submit" className="mt-6 w-full p-3 bg-teal-500 text-white rounded-lg font-semibold hover:bg-teal-600 disabled:bg-gray-400" disabled={isLoading}>
                {isLoading ? "Creating..." : "Create Admin"}
              </button>
            </form>
          </motion.div>
        );
      case "doctors":
        return (
          <motion.div variants={contentVariants} initial="hidden" animate="visible" className="bg-white p-6 rounded-lg shadow-lg border border-gray-200">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">Doctors</h2>
            {doctors.length === 0 ? (
              <p className="text-gray-600">No doctors available.</p>
            ) : (
              <table className="w-full text-left">
                <thead>
                  <tr className="border-b">
                    <th className="py-2 px-4 text-gray-700 font-semibold">Username</th>
                    <th className="py-2 px-4 text-gray-700 font-semibold">Email</th>
                    <th className="py-2 px-4 text-gray-700 font-semibold">Department</th>
                    <th className="py-2 px-4 text-gray-700 font-semibold">Specialty</th>
                    <th className="py-2 px-4 text-gray-700 font-semibold">Title</th>
                    <th className="py-2 px-4 text-gray-700 font-semibold">Phone</th>
                    <th className="py-2 px-4 text-gray-700 font-semibold">Bio</th>
                    <th className="py-2 px-4 text-gray-700 font-semibold">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {doctors.map((doctor) => (
                    <tr key={doctor.user_id} className="border-b">
                      <td className="py-2 px-4">{doctor.username}</td>
                      <td className="py-2 px-4">{doctor.email}</td>
                      <td className="py-2 px-4">{doctor.department_name}</td>
                      <td className="py-2 px-4">{doctor.specialty}</td>
                      <td className="py-2 px-4">{doctor.title}</td>
                      <td className="py-2 px-4">{doctor.phone || "N/A"}</td>
                      <td className="py-2 px-4">{doctor.bio || "N/A"}</td>
                      <td className="py-2 px-4">
                        <button onClick={() => handleDeleteDoctor(doctor.user_id)} className="text-red-500 hover:text-red-600" title="Delete" disabled={isLoading}>
                          <FaTrash />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
            {deleteDoctorMessage && <p className="text-green-500 text-sm mt-4">{deleteDoctorMessage}</p>}
            {deleteDoctorError && <p className="text-red-500 text-sm mt-4">{deleteDoctorError}</p>}
          </motion.div>
        );
      case "departments":
        return (
          <motion.div variants={contentVariants} initial="hidden" animate="visible" className="bg-white p-6 rounded-lg shadow-lg border border-gray-200">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">Departments</h2>
            {departments.length === 0 ? (
              <p className="text-gray-600">No departments available.</p>
            ) : (
              <table className="w-full text-left">
                <thead>
                  <tr className="border-b">
                    <th className="py-2 px-4 text-gray-700 font-semibold">Name</th>
                    <th className="py-2 px-4 text-gray-700 font-semibold">Hospital</th>
                  </tr>
                </thead>
                <tbody>
                  {departments.map((dept) => (
                    <tr key={dept.id} className="border-b">
                      <td className="py-2 px-4">{dept.name}</td>
                      <td className="py-2 px-4">{dept.hospital_name}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </motion.div>
        );
      case "appointments":
        return (
          <motion.div variants={contentVariants} initial="hidden" animate="visible" className="bg-white p-6 rounded-lg shadow-lg border border-gray-200">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">Appointments</h2>
            {appointments.length === 0 ? (
              <p className="text-gray-600">No appointments available.</p>
            ) : (
              <table className="w-full text-left">
                <thead>
                  <tr className="border-b">
                    <th className="py-2 px-4 text-gray-700 font-semibold">Patient</th>
                    <th className="py-2 px-4 text-gray-700 font-semibold">Doctor</th>
                    <th className="py-2 px-4 text-gray-700 font-semibold">Department</th>
                    <th className="py-2 px-4 text-gray-700 font-semibold">Date</th>
                    <th className="py-2 px-4 text-gray-700 font-semibold">Time</th>
                    <th className="py-2 px-4 text-gray-700 font-semibold">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {appointments.map((appt) => (
                    <tr key={appt.id} className="border-b">
                      <td className="py-2 px-4">{appt.username}</td>
                      <td className="py-2 px-4">{appt.doctor_username}</td>
                      <td className="py-2 px-4">{appt.department_name}</td>
                      <td className="py-2 px-4">{appt.appointment_date}</td>
                      <td className="py-2 px-4">{`${appt.start_time} - ${appt.end_time}`}</td>
                      <td className="py-2 px-4">{appt.status}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </motion.div>
        );
      default:
        return null;
    }
  };

  return <div>{renderContent()}</div>;
};

// Main Dashboard Component
const SuperAdminDashboard = () => {
  const { user, token } = useAuth();
  const [activeSection, setActiveSection] = useState("welcome");
  const [hospitals, setHospitals] = useState([]);
  const [admins, setAdmins] = useState([]);
  const [doctors, setDoctors] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [appointments, setAppointments] = useState([]);
  const [hospitalForm, setHospitalForm] = useState({
    name: "",
    address: "",
    lat: "",
    lng: "",
  });
  const [adminForm, setAdminForm] = useState({
    hospital_id: "",
    admin_id: "",
  });
  const [createAdminForm, setCreateAdminForm] = useState({
    username: "",
    email: "",
    password: "",
    hospital_id: "",
  });
  const [editHospitalForm, setEditHospitalForm] = useState({
    id: "",
    name: "",
    address: "",
    lat: "",
    lng: "",
  });
  const [hospitalMessage, setHospitalMessage] = useState("");
  const [hospitalError, setHospitalError] = useState("");
  const [adminMessage, setAdminMessage] = useState("");
  const [adminError, setAdminError] = useState("");
  const [createAdminMessage, setCreateAdminMessage] = useState("");
  const [createAdminError, setCreateAdminError] = useState("");
  const [updateHospitalMessage, setUpdateHospitalMessage] = useState("");
  const [updateHospitalError, setUpdateHospitalError] = useState("");
  const [deleteHospitalMessage, setDeleteHospitalMessage] = useState("");
  const [deleteHospitalError, setDeleteHospitalError] = useState("");
  const [deleteAdminMessage, setDeleteAdminMessage] = useState("");
  const [deleteAdminError, setDeleteAdminError] = useState("");
  const [deleteDoctorMessage, setDeleteDoctorMessage] = useState("");
  const [deleteDoctorError, setDeleteDoctorError] = useState("");
  const [isLoading, setIsLoading] = useState(false); // New state for loading

  // Clear messages after 5 seconds
  useEffect(() => {
    const timers = [];
    if (hospitalMessage) timers.push(setTimeout(() => setHospitalMessage(""), 5000));
    if (hospitalError) timers.push(setTimeout(() => setHospitalError(""), 5000));
    if (adminMessage) timers.push(setTimeout(() => setAdminMessage(""), 5000));
    if (adminError) timers.push(setTimeout(() => setAdminError(""), 5000));
    if (createAdminMessage) timers.push(setTimeout(() => setCreateAdminMessage(""), 5000));
    if (createAdminError) timers.push(setTimeout(() => setCreateAdminError(""), 5000));
    if (updateHospitalMessage) timers.push(setTimeout(() => setUpdateHospitalMessage(""), 5000));
    if (updateHospitalError) timers.push(setTimeout(() => setUpdateHospitalError(""), 5000));
    if (deleteHospitalMessage) timers.push(setTimeout(() => setDeleteHospitalMessage(""), 5000));
    if (deleteHospitalError) timers.push(setTimeout(() => setDeleteHospitalError(""), 5000));
    if (deleteAdminMessage) timers.push(setTimeout(() => setDeleteAdminMessage(""), 5000));
    if (deleteAdminError) timers.push(setTimeout(() => setDeleteAdminError(""), 5000));
    if (deleteDoctorMessage) timers.push(setTimeout(() => setDeleteDoctorMessage(""), 5000));
    if (deleteDoctorError) timers.push(setTimeout(() => setDeleteDoctorError(""), 5000));
    return () => timers.forEach(clearTimeout);
  }, [hospitalMessage, hospitalError, adminMessage, adminError, createAdminMessage, createAdminError, updateHospitalMessage, updateHospitalError, deleteHospitalMessage, deleteHospitalError, deleteAdminMessage, deleteAdminError, deleteDoctorMessage, deleteDoctorError]);

  // Fetch all data
  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      try {
        const [hospitalsRes, adminsRes, appointmentsRes, departmentsRes, doctorsRes] = await Promise.all([
          axios.get("http://localhost:8000/api/hospitals", { headers: { Authorization: `Bearer ${token}` } }),
          axios.get("http://localhost:8000/api/admins", { headers: { Authorization: `Bearer ${token}` } }),
          axios.get("http://localhost:8000/api/appointments", { headers: { Authorization: `Bearer ${token}` } }),
          axios.get("http://localhost:8000/api/departments", { headers: { Authorization: `Bearer ${token}` } }),
          axios.get("http://localhost:8000/api/doctors", { headers: { Authorization: `Bearer ${token}` } }),
        ]);
        setHospitals(hospitalsRes.data);
        setAdmins(adminsRes.data);
        setAppointments(appointmentsRes.data);
        setDepartments(departmentsRes.data);
        setDoctors(doctorsRes.data);
      } catch (error) {
        console.error("Error fetching data:", error);
        setHospitalError("Failed to load data. Please try again.");
      } finally {
        setIsLoading(false);
      }
    };
    if (token) fetchData();
  }, [token]);

  // Handle hospital form submission (create)
  const handleHospitalSubmit = async (e) => {
    e.preventDefault();
    setHospitalMessage("");
    setHospitalError("");
    setIsLoading(true);
    try {
      const response = await fetch("http://localhost:8000/api/hospitals", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          name: hospitalForm.name,
          address: hospitalForm.address,
          lat: parseFloat(hospitalForm.lat),
          lng: parseFloat(hospitalForm.lng),
        }),
      });
      const data = await response.json();
      if (response.ok) {
        setHospitalMessage("Hospital added successfully!");
        setHospitalForm({ name: "", address: "", lat: "", lng: "" });
        const hospitalResponse = await fetch("http://localhost:8000/api/hospitals", {
          headers: { Authorization: `Bearer ${token}` },
        });
        const hospitalData = await hospitalResponse.json();
        if (hospitalResponse.ok) setHospitals(hospitalData);
      } else {
        setHospitalError(data.detail || "Failed to add hospital");
      }
    } catch (err) {
      setHospitalError("Error adding hospital: " + err.message);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle hospital update
  const handleUpdateHospital = async (e, hospitalId) => {
    e.preventDefault();
    setUpdateHospitalMessage("");
    setUpdateHospitalError("");
    setIsLoading(true);
    try {
      const response = await fetch(`http://localhost:8000/api/hospitals/${hospitalId}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          name: editHospitalForm.name,
          address: editHospitalForm.address,
          lat: parseFloat(editHospitalForm.lat),
          lng: parseFloat(editHospitalForm.lng),
        }),
      });
      const data = await response.json();
      if (response.ok) {
        setUpdateHospitalMessage("Hospital updated successfully!");
        setEditHospitalForm({ id: "", name: "", address: "", lat: "", lng: "" });
        const hospitalResponse = await fetch("http://localhost:8000/api/hospitals", {
          headers: { Authorization: `Bearer ${token}` },
        });
        const hospitalData = await hospitalResponse.json();
        if (hospitalResponse.ok) setHospitals(hospitalData);
        setActiveSection("hospitals");
      } else {
        setUpdateHospitalError(data.detail || "Failed to update hospital");
      }
    } catch (err) {
      setUpdateHospitalError("Error updating hospital: " + err.message);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle hospital deletion
  const handleDeleteHospital = async (hospitalId) => {
    if (!window.confirm("Are you sure you want to delete this hospital?")) return;
    setDeleteHospitalMessage("");
    setDeleteHospitalError("");
    setIsLoading(true);
    try {
      const response = await fetch(`http://localhost:8000/api/hospitals/${hospitalId}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      const data = await response.json();
      if (response.ok) {
        setDeleteHospitalMessage("Hospital deleted successfully!");
        const hospitalResponse = await fetch("http://localhost:8000/api/hospitals", {
          headers: { Authorization: `Bearer ${token}` },
        });
        const hospitalData = await hospitalResponse.json();
        if (hospitalResponse.ok) setHospitals(hospitalData);
      } else {
        setDeleteHospitalError(data.detail || "Failed to delete hospital");
      }
    } catch (err) {
      setDeleteHospitalError("Error deleting hospital: " + err.message);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle admin deletion
  const handleDeleteAdmin = async (adminId) => {
    if (!window.confirm("Are you sure you want to delete this admin?")) return;
    setDeleteAdminMessage("");
    setDeleteAdminError("");
    setIsLoading(true);
    try {
      const response = await fetch(`http://localhost:8000/api/admins/${adminId}`, {
        // Updated endpoint
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      const data = await response.json();
      if (response.ok) {
        setDeleteAdminMessage(data.detail || "Admin deleted successfully!"); // Use backend response
        const adminResponse = await fetch("http://localhost:8000/api/admins", {
          headers: { Authorization: `Bearer ${token}` },
        });
        const adminData = await adminResponse.json();
        if (adminResponse.ok) setAdmins(adminData);
      } else {
        setDeleteAdminError(data.detail || "Failed to delete admin");
      }
    } catch (err) {
      setDeleteAdminError("Error deleting admin: " + err.message);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle doctor deletion
  const handleDeleteDoctor = async (doctorId) => {
    if (!window.confirm("Are you sure you want to delete this doctor?")) return;
    setDeleteDoctorMessage("");
    setDeleteDoctorError("");
    setIsLoading(true);
    try {
      const response = await fetch(`http://localhost:8000/api/doctors/${doctorId}`, {
        // Updated endpoint
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      const data = await response.json();
      if (response.ok) {
        setDeleteDoctorMessage(data.detail || "Doctor deleted successfully!"); // Use backend response
        const doctorResponse = await fetch("http://localhost:8000/api/doctors", {
          headers: { Authorization: `Bearer ${token}` },
        });
        const doctorData = await doctorResponse.json();
        if (doctorResponse.ok) setDoctors(doctorData);
      } else {
        setDeleteDoctorError(data.detail || "Failed to delete doctor");
      }
    } catch (err) {
      setDeleteDoctorError("Error deleting doctor: " + err.message);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle admin assignment form submission
  const handleAdminSubmit = async (e) => {
    e.preventDefault();
    setAdminMessage("");
    setAdminError("");
    setIsLoading(true);
    try {
      const response = await fetch(`http://localhost:8000/api/hospitals/${adminForm.hospital_id}/assign_admin`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          user_id: adminForm.admin_id,
        }),
      });
      const data = await response.json();
      if (response.ok) {
        setAdminMessage(data.detail || "Admin assigned successfully!");
        setAdminForm({ hospital_id: "", admin_id: "" });
        const adminResponse = await fetch("http://localhost:8000/api/admins", {
          headers: { Authorization: `Bearer ${token}` },
        });
        const adminData = await adminResponse.json();
        if (adminResponse.ok) setAdmins(adminData);
      } else {
        setAdminError(data.detail || "Failed to assign admin");
      }
    } catch (err) {
      setAdminError("Error assigning admin: " + err.message);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle create admin form submission
  const handleCreateAdminSubmit = async (e) => {
    e.preventDefault();
    setCreateAdminMessage("");
    setCreateAdminError("");
    setIsLoading(true);
    try {
      const response = await fetch("http://localhost:8000/api/admins", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          username: createAdminForm.username,
          email: createAdminForm.email,
          password: createAdminForm.password,
          hospital_id: createAdminForm.hospital_id || null,
        }),
      });
      const data = await response.json();
      if (response.ok) {
        setCreateAdminMessage("Admin created successfully!");
        setCreateAdminForm({ username: "", email: "", password: "", hospital_id: "" });
        const adminResponse = await fetch("http://localhost:8000/api/admins", {
          headers: { Authorization: `Bearer ${token}` },
        });
        const adminData = await adminResponse.json();
        if (adminResponse.ok) setAdmins(adminData);
      } else {
        setCreateAdminError(data.detail || "Failed to create admin");
      }
    } catch (err) {
      setCreateAdminError("Error creating admin: " + err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const dashboardCards = [
    { name: "View Hospitals", icon: <FaHospital className="text-3xl" />, section: "hospitals", description: "List, update, or delete hospitals" },
    { name: "Add Hospital", icon: <FaHospital className="text-3xl" />, section: "add-hospital", description: "Create a new hospital" },
    { name: "View Admins", icon: <FaUserShield className="text-3xl" />, section: "admins", description: "List or delete admins" },
    { name: "Assign Admin", icon: <FaUserShield className="text-3xl" />, section: "assign-admin", description: "Assign admin to hospital" },
    { name: "Create Admin", icon: <FaUserPlus className="text-3xl" />, section: "create-admin", description: "Create a new admin user" },
    { name: "View Doctors", icon: <FaUserMd className="text-3xl" />, section: "doctors", description: "List or delete doctors" },
    { name: "View Departments", icon: <FaBuilding className="text-3xl" />, section: "departments", description: "List all departments" },
    { name: "View Appointments", icon: <FaCalendar className="text-3xl" />, section: "appointments", description: "List all appointments" },
  ];

  const cardVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.5 } },
    hover: { scale: 1.05, transition: { duration: 0.3 } },
  };

  return (
    <div className="flex flex-col min-h-screen bg-gray-100">
      <NavBar />
      <main className="flex-1 py-12 px-4">
        <div className="max-w-7xl mx-auto">
          <motion.div className="flex justify-between items-center mb-8" initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }}>
            <h1 className="text-3xl font-bold text-gray-800">
              Super Admin Dashboard, <span className="text-teal-500">{user?.username || "Super Admin"}</span>!
            </h1>
          </motion.div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
            {dashboardCards.map((card, index) => (
              <motion.div key={card.section} className="bg-white rounded-xl shadow-lg p-6 flex flex-col items-center text-center cursor-pointer border border-gray-200 hover:border-teal-500" variants={cardVariants} initial="hidden" animate="visible" whileHover="hover" transition={{ delay: index * 0.1 }} onClick={() => setActiveSection(card.section)} disabled={isLoading}>
                <div className="text-teal-500 mb-4">{card.icon}</div>
                <h2 className="text-xl font-semibold text-gray-800 mb-2">{card.name}</h2>
                <p className="text-gray-600">{card.description}</p>
              </motion.div>
            ))}
          </div>

          <SuperAdminContent
            activeSection={activeSection}
            hospitals={hospitals}
            admins={admins}
            doctors={doctors}
            departments={departments}
            appointments={appointments}
            hospitalForm={hospitalForm}
            setHospitalForm={setHospitalForm}
            adminForm={adminForm}
            setAdminForm={setAdminForm}
            createAdminForm={createAdminForm}
            setCreateAdminForm={setCreateAdminForm}
            editHospitalForm={editHospitalForm}
            setEditHospitalForm={setEditHospitalForm}
            handleHospitalSubmit={handleHospitalSubmit}
            handleAdminSubmit={handleAdminSubmit}
            handleCreateAdminSubmit={handleCreateAdminSubmit}
            handleUpdateHospital={handleUpdateHospital}
            handleDeleteHospital={handleDeleteHospital}
            handleDeleteAdmin={handleDeleteAdmin}
            handleDeleteDoctor={handleDeleteDoctor}
            hospitalMessage={hospitalMessage}
            hospitalError={hospitalError}
            adminMessage={adminMessage}
            adminError={adminError}
            createAdminMessage={createAdminMessage}
            createAdminError={createAdminError}
            updateHospitalMessage={updateHospitalMessage}
            updateHospitalError={updateHospitalError}
            deleteHospitalMessage={deleteHospitalMessage}
            deleteHospitalError={deleteHospitalError}
            deleteAdminMessage={deleteAdminMessage}
            deleteAdminError={deleteAdminError}
            deleteDoctorMessage={deleteDoctorMessage}
            deleteDoctorError={deleteDoctorError}
            setActiveSection={setActiveSection}
            isLoading={isLoading} // Pass loading state
          />
        </div>
      </main>
      <Footer />
    </div>
  );
};

export default SuperAdminDashboard;
