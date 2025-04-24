import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import NavBar from "../components/layout/NavBar";
import { useAuth } from "../context/AuthContext";
import { FaHospital, FaBuilding, FaUserMd, FaHeart } from "react-icons/fa";

// Footer Component (reused from SuperAdminDashboard)
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
const AdminContent = ({ activeSection, hospital, departments, doctors, departmentForm, setDepartmentForm, doctorForm, setDoctorForm, handleDepartmentSubmit, handleDoctorSubmit, departmentMessage, departmentError, doctorMessage, doctorError }) => {
  const contentVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.5 } },
  };

  const renderContent = () => {
    switch (activeSection) {
      case "welcome":
        return (
          <motion.div variants={contentVariants} initial="hidden" animate="visible">
            <p className="text-gray-600">Welcome to the Admin Dashboard. Use the cards above to manage your hospital, departments, and doctors.</p>
          </motion.div>
        );
      case "view-hospital":
        return (
          <motion.div variants={contentVariants} initial="hidden" animate="visible" className="bg-white p-6 rounded-lg shadow-lg border border-gray-200">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">Assigned Hospital</h2>
            {hospital ? (
              <div className="space-y-2">
                <p>
                  <strong>Name:</strong> {hospital.name}
                </p>
                <p>
                  <strong>Address:</strong> {hospital.address}
                </p>
                <p>
                  <strong>Latitude:</strong> {hospital.lat}
                </p>
                <p>
                  <strong>Longitude:</strong> {hospital.lng}
                </p>
              </div>
            ) : (
              <p className="text-red-500 text-sm">No hospital assigned.</p>
            )}
          </motion.div>
        );
      case "add-department":
        return (
          <motion.div variants={contentVariants} initial="hidden" animate="visible" className="bg-white p-6 rounded-lg shadow-lg border border-gray-200">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">Add Department</h2>
            {hospital ? (
              <form onSubmit={handleDepartmentSubmit}>
                <div className="space-y-4">
                  <div>
                    <label className="block text-gray-700 text-sm font-semibold mb-2">Department Name</label>
                    <input type="text" value={departmentForm.name} onChange={(e) => setDepartmentForm({ ...departmentForm, name: e.target.value })} className="w-full p-3 rounded-lg border border-gray-300 focus:outline-none focus:border-teal-500" placeholder="e.g., Cardiology" required />
                  </div>
                </div>
                {departmentMessage && <p className="text-green-500 text-sm mt-4">{departmentMessage}</p>}
                {departmentError && <p className="text-red-500 text-sm mt-4">{departmentError}</p>}
                <button type="submit" className="mt-6 w-full p-3 bg-teal-500 text-white rounded-lg font-semibold hover:bg-teal-600">
                  Add Department
                </button>
              </form>
            ) : (
              <p className="text-red-500 text-sm">Assign a hospital to add departments.</p>
            )}
          </motion.div>
        );
      case "create-doctor":
        return (
          <motion.div variants={contentVariants} initial="hidden" animate="visible" className="bg-white p-6 rounded-lg shadow-lg border border-gray-200">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">Create Doctor</h2>
            {departments.length === 0 || !hospital ? (
              <p className="text-red-500 text-sm">{hospital ? "No departments available. Add a department first." : "Assign a hospital to add doctors."}</p>
            ) : (
              <form onSubmit={handleDoctorSubmit}>
                <div className="space-y-4">
                  <div>
                    <label className="block text-gray-700 text-sm font-semibold mb-2">Department</label>
                    <select value={doctorForm.department_id} onChange={(e) => setDoctorForm({ ...doctorForm, department_id: e.target.value })} className="w-full p-3 rounded-lg border border-gray-300 focus:outline-none focus:border-teal-500" required>
                      <option value="">Select Department</option>
                      {departments.map((dept) => (
                        <option key={dept.id} value={dept.id}>
                          {dept.name}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-gray-700 text-sm font-semibold mb-2">Username</label>
                    <input type="text" value={doctorForm.username} onChange={(e) => setDoctorForm({ ...doctorForm, username: e.target.value })} className="w-full p-3 rounded-lg border border-gray-300 focus:outline-none focus:border-teal-500" placeholder="e.g., DrDerma" required />
                  </div>
                  <div>
                    <label className="block text-gray-700 text-sm font-semibold mb-2">Email</label>
                    <input type="email" value={doctorForm.email} onChange={(e) => setDoctorForm({ ...doctorForm, email: e.target.value })} className="w-full p-3 rounded-lg border border-gray-300 focus:outline-none focus:border-teal-500" placeholder="e.g., drderma@example.com" required />
                  </div>
                  <div>
                    <label className="block text-gray-700 text-sm font-semibold mb-2">Password</label>
                    <input type="password" value={doctorForm.password} onChange={(e) => setDoctorForm({ ...doctorForm, password: e.target.value })} className="w-full p-3 rounded-lg border border-gray-300 focus:outline-none focus:border-teal-500" placeholder="Enter password" required />
                  </div>
                  <div>
                    <label className="block text-gray-700 text-sm font-semibold mb-2">Specialty</label>
                    <input type="text" value={doctorForm.specialty} onChange={(e) => setDoctorForm({ ...doctorForm, specialty: e.target.value })} className="w-full p-3 rounded-lg border border-gray-300 focus:outline-none focus:border-teal-500" placeholder="e.g., Dermatology" required />
                  </div>
                  <div>
                    <label className="block text-gray-700 text-sm font-semibold mb-2">Title</label>
                    <input type="text" value={doctorForm.title} onChange={(e) => setDoctorForm({ ...doctorForm, title: e.target.value })} className="w-full p-3 rounded-lg border border-gray-200 focus:outline-none focus:border-teal-500" placeholder="e.g., MD" required />
                  </div>
                  <div>
                    <label className="block text-gray-700 text-sm font-semibold mb-2">Phone</label>
                    <input type="text" value={doctorForm.phone} onChange={(e) => setDoctorForm({ ...doctorForm, phone: e.target.value })} className="w-full p-3 rounded-lg border border-gray-300 focus:outline-none focus:border-teal-500" placeholder="e.g., 555-123-4567" />
                  </div>
                  <div>
                    <label className="block text-gray-700 text-sm font-semibold mb-2">Bio</label>
                    <textarea value={doctorForm.bio} onChange={(e) => setDoctorForm({ ...doctorForm, bio: e.target.value })} className="w-full p-3 rounded-lg border border-gray-300 focus:outline-none focus:border-teal-500" placeholder="e.g., Experienced dermatologist" rows="4" />
                  </div>
                </div>
                {doctorMessage && <p className="text-green-500 text-sm mt-4">{doctorMessage}</p>}
                {doctorError && <p className="text-red-500 text-sm mt-4">{doctorError}</p>}
                <button type="submit" className="mt-6 w-full p-3 bg-teal-500 text-white rounded-lg font-semibold hover:bg-teal-600 disabled:bg-gray-400" disabled={departments.length === 0 || !hospital}>
                  Create Doctor
                </button>
              </form>
            )}
          </motion.div>
        );
      case "view-departments":
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
                  </tr>
                </thead>
                <tbody>
                  {departments.map((dept) => (
                    <tr key={dept.id} className="border-b">
                      <td className="py-2 px-4">{dept.name}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </motion.div>
        );
      case "view-doctors":
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
                  </tr>
                </thead>
                <tbody>
                  {doctors.map((doc) => (
                    <tr key={doc.user_id} className="border-b">
                      <td className="py-2 px-4">{doc.username}</td>
                      <td className="py-2 px-4">{doc.email}</td>
                      <td className="py-2 px-4">{doc.department_name}</td>
                      <td className="py-2 px-4">{doc.specialty}</td>
                      <td className="py-2 px-4">{doc.title}</td>
                      <td className="py-2 px-4">{doc.phone || "N/A"}</td>
                      <td className="py-2 px-4">{doc.bio || "N/A"}</td>
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
const AdminDashboard = () => {
  const { user, token } = useAuth();
  const [activeSection, setActiveSection] = useState("welcome");
  const [hospital, setHospital] = useState(null);
  const [departments, setDepartments] = useState([]);
  const [doctors, setDoctors] = useState([]);
  const [departmentForm, setDepartmentForm] = useState({ name: "" });
  const [doctorForm, setDoctorForm] = useState({
    department_id: "",
    username: "",
    email: "",
    password: "",
    specialty: "",
    title: "",
    phone: "",
    bio: "",
  });
  const [departmentMessage, setDepartmentMessage] = useState("");
  const [doctorMessage, setDoctorMessage] = useState("");
  const [departmentError, setDepartmentError] = useState("");
  const [doctorError, setDoctorError] = useState("");

  // Fetch hospital, departments, and doctors
  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch hospital
        const hospitalResponse = await fetch("http://localhost:8000/api/admin/hospital", {
          headers: { Authorization: `Bearer ${token}` },
        });
        const hospitalData = await hospitalResponse.json();
        if (hospitalResponse.ok) {
          setHospital(hospitalData);
        } else {
          console.error("Failed to fetch hospital:", hospitalData.detail);
        }

        // Fetch departments
        const departmentResponse = await fetch("http://localhost:8000/api/departments", {
          headers: { Authorization: `Bearer ${token}` },
        });
        const departmentData = await departmentResponse.json();
        if (departmentResponse.ok) {
          setDepartments(departmentData);
        } else {
          console.error("Failed to fetch departments:", departmentData.detail);
        }

        // Fetch doctors
        const doctorResponse = await fetch("http://localhost:8000/api/doctors", {
          headers: { Authorization: `Bearer ${token}` },
        });
        const doctorData = await doctorResponse.json();
        if (doctorResponse.ok) {
          setDoctors(doctorData);
        } else {
          console.error("Failed to fetch doctors:", doctorData.detail);
        }
      } catch (err) {
        console.error("Error fetching data:", err);
      }
    };
    if (token) fetchData();
  }, [token]);

  // Handle department form submission
  const handleDepartmentSubmit = async (e) => {
    e.preventDefault();
    setDepartmentMessage("");
    setDepartmentError("");
    try {
      const response = await fetch("http://localhost:8000/api/departments", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(departmentForm),
      });
      const data = await response.json();
      if (response.ok) {
        setDepartmentMessage("Department added successfully!");
        setDepartmentForm({ name: "" });
        const departmentResponse = await fetch("http://localhost:8000/api/departments", {
          headers: { Authorization: `Bearer ${token}` },
        });
        const departmentData = await departmentResponse.json();
        if (departmentResponse.ok) setDepartments(departmentData);
      } else {
        setDepartmentError(data.detail || "Failed to add department");
      }
    } catch (err) {
      setDepartmentError("Error adding department: " + err.message);
    }
  };

  // Handle doctor form submission
  const handleDoctorSubmit = async (e) => {
    e.preventDefault();
    setDoctorMessage("");
    setDoctorError("");
    try {
      const response = await fetch("http://localhost:8000/api/doctors", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(doctorForm),
      });
      const data = await response.json();
      if (response.ok) {
        setDoctorMessage(data.message);
        setDoctorForm({
          department_id: "",
          username: "",
          email: "",
          password: "",
          specialty: "",
          title: "",
          phone: "",
          bio: "",
        });
        const doctorResponse = await fetch("http://localhost:8000/api/doctors", {
          headers: { Authorization: `Bearer ${token}` },
        });
        const doctorData = await doctorResponse.json();
        if (doctorResponse.ok) setDoctors(doctorData);
      } else {
        setDoctorError(data.detail || "Failed to create doctor");
      }
    } catch (err) {
      setDoctorError("Error creating doctor: " + err.message);
    }
  };

  const dashboardCards = [
    { name: "View Hospital", icon: <FaHospital className="text-3xl" />, section: "view-hospital", description: "View assigned hospital details" },
    { name: "Add Department", icon: <FaBuilding className="text-3xl" />, section: "add-department", description: "Create a new department" },
    { name: "Create Doctor", icon: <FaUserMd className="text-3xl" />, section: "create-doctor", description: "Add a new doctor" },
    { name: "View Departments", icon: <FaBuilding className="text-3xl" />, section: "view-departments", description: "List all departments" },
    { name: "View Doctors", icon: <FaUserMd className="text-3xl" />, section: "view-doctors", description: "List all doctors" },
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
              Admin Dashboard, <span className="text-teal-500">{user?.username || "Admin"}</span>!
            </h1>
          </motion.div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
            {dashboardCards.map((card, index) => (
              <motion.div key={card.section} className="bg-white rounded-xl shadow-lg p-6 flex flex-col items-center text-center cursor-pointer border border-gray-200 hover:border-teal-500" variants={cardVariants} initial="hidden" animate="visible" whileHover="hover" transition={{ delay: index * 0.1 }} onClick={() => setActiveSection(card.section)}>
                <div className="text-teal-500 mb-4">{card.icon}</div>
                <h2 className="text-xl font-semibold text-gray-800 mb-2">{card.name}</h2>
                <p className="text-gray-600">{card.description}</p>
              </motion.div>
            ))}
          </div>

          <AdminContent activeSection={activeSection} hospital={hospital} departments={departments} doctors={doctors} departmentForm={departmentForm} setDepartmentForm={setDepartmentForm} doctorForm={doctorForm} setDoctorForm={setDoctorForm} handleDepartmentSubmit={handleDepartmentSubmit} handleDoctorSubmit={handleDoctorSubmit} departmentMessage={departmentMessage} departmentError={departmentError} doctorMessage={doctorMessage} doctorError={doctorError} />
        </div>
      </main>
      <Footer />
    </div>
  );
};

export default AdminDashboard;
