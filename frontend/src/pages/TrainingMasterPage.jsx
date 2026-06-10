import React, { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import MainLayout from "../components/MainLayout";
import api from "../api/axios";
import { getUserFromToken } from "../utils/auth";
import Toast from "../components/Toast";
import ConfirmModal from "../components/ConfirmModal";
import * as XLSX from 'xlsx';
import YearPicker from "../components/YearPicker";


export default function TrainingMasterPage() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [trainings, setTrainings] = useState([]);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const [loading, setLoading] = useState(true);

  // Filters
  const [search, setSearch] = useState("");
  const [division, setDivision] = useState("");
  const [month, setMonth] = useState("");
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear().toString());
  const [activeView, setActiveView] = useState("admin");

  // Lookup tables
  const [divisions, setDivisions] = useState([]);
  const [employees, setEmployees] = useState([]);
  const [courseCategories, setCourseCategories] = useState([]);
  const [courses, setCourses] = useState([]);
  const [vendors, setVendors] = useState([]);

  // Modals & Tabs
  const [showModal, setShowModal] = useState(false);
  const [showEventModal, setShowEventModal] = useState(false);
  const [showReportModal, setShowReportModal] = useState(false);
  const [activeTab, setActiveTab] = useState("location");
  const [activeReportTab, setActiveReportTab] = useState("master");
  const [isEditMode, setIsEditMode] = useState(false);
  const [editingId, setEditingId] = useState(null);

  // Budget Modal State
  const [showBudgetModal, setShowBudgetModal] = useState(false);
  const [budgetName, setBudgetName] = useState("");
  const [budgetStartDate, setBudgetStartDate] = useState("");
  const [budgetEndDate, setBudgetEndDate] = useState("");
  const [totalBudget, setTotalBudget] = useState("");

  // ─── UI State ───────────────────────────────────────────────────────
  const [toast, setToast] = useState(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  // Form states mapping alpine to React arrays
  const [trainingCode, setTrainingCode] = useState("");
  const [trainingType, setTrainingType] = useState("Inhouse Training");
  const [trainingCategory, setTrainingCategory] = useState("Soft Skill");
  const [courseCategory, setCourseCategory] = useState("");
  const [courseId, setCourseId] = useState("");
  const [trainingTitle, setTrainingTitle] = useState("");
  const [trainingDescription, setTrainingDescription] = useState("");
  const [pic, setPic] = useState("");
  const [vendorId, setVendorId] = useState("");
  const [estimatedCost, setEstimatedCost] = useState("");

  const [topic, setTopic] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [status, setStatus] = useState("Draft");

  const [locationCity, setLocationCity] = useState("");
  const [venue, setVenue] = useState("");
  const [room, setRoom] = useState("");
  const [address, setAddress] = useState("");

  const [scheduleRows, setScheduleRows] = useState([
    { date: "", start: "", end: "", material: "", instructor: "" },
  ]);

  const [participantRows, setParticipantRows] = useState([
    { employee: "", attendance: "Present", l1: "", l2: "" },
  ]);

  const [evaluation, setEvaluation] = useState({
    courseAccess: false,
    feedback: false,
    evaluationStage: false,
  });

  const [costRows, setCostRows] = useState([]);
  const [documentationRows, setDocumentationRows] = useState([]);
  const [costAllocationType, setCostAllocationType] = useState("Estimate Cost");

  const getAbbreviation = (text) => {
    if (!text) return "";
    return text.split(" ").filter(w => w.length > 0).map(w => w[0].toUpperCase()).join("");
  };

  const isManagerialRole = user && ['Super Administrator', 'Administrator', 'Dean', 'Head of Division', 'Team Leader'].includes(user.role);
  const isAdmin = user && ['Super Administrator', 'Administrator', 'Dean'].includes(user.role) && activeView === 'admin';

  // ================= FETCH DATA =================
  const fetchTrainings = useCallback(async () => {
    setLoading(true);
    try {
      const res = await api.get(
        `/api/training-master/?page=${page}&search=${search}&division=${division}&month=${month}&year=${selectedYear}&view_mode=${activeView}`
      );
      if (res && res.data) {
        // Handling both DRF results object and raw list
        const results = res.data.results || res.data;
        const count = res.data.count || (Array.isArray(res.data) ? res.data.length : results.length);
        setTrainings(results || []);
        setTotalCount(count);
        setTotalPages(Math.ceil(count / 50) || 1);
      }
    } catch (e) {
      console.warn("API Error during fetchTrainings", e);
    } finally {
      setLoading(false);
    }
  }, [page, search, division, month, selectedYear, activeView]);

  const fetchData = async () => {
    try {
      const [divs, emps, cats, vends] = await Promise.all([
        api.get("/api/divisions/"),
        api.get("/api/employee/?nopage=true"),
        api.get("/api/course-categories/"),
        api.get("/api/vendors/")
      ]);

      setDivisions(divs.data);
      const sortedEmps = (Array.isArray(emps.data) ? emps.data : (emps.data.results || []))
        .sort((a, b) => (a.full_name || '').localeCompare(b.full_name || ''));
      setEmployees(sortedEmps);
      setCourseCategories(cats.data);
      setVendors(vends.data);
    } catch (e) {
      console.warn("API Error during lookup fetch", e);
    }
  };

  const fetchCourses = async (categoryId = "") => {
    try {
      const url = categoryId ? `/api/courses/?category_id=${categoryId}` : "/api/courses/";
      const res = await api.get(url);
      if (res && res.data) setCourses(res.data);
    } catch (e) {
      console.warn("API Error during fetchCourses", e);
    }
  };

  useEffect(() => {
    const userData = getUserFromToken();
    if (userData) {
      setUser(userData);
      const isManagerial = ['Super Administrator', 'Administrator', 'Dean', 'Head of Division', 'Team Leader'].includes(userData.role);
      if (!isManagerial) {
        setActiveView('employee');
      }
    }
    fetchData();
  }, []);

  useEffect(() => {
    fetchTrainings();
  }, [fetchTrainings]);

  useEffect(() => {
    if (courseCategory) fetchCourses(courseCategory);
  }, [courseCategory]);

  const checkTrainingCode = async (code) => {
    if (!code) return;
    try {
      const res = await api.get(`/api/check-training-code/?code=${code}${editingId ? `&exclude_id=${editingId}` : ''}`);
      if (res.data.exists) {
        setToast({ message: "Training code already existed", type: "error" });
      }
    } catch (e) {
      console.warn("Check training code failed", e);
    }
  };

  const handleEmployeeChange = async (idx, nik) => {
    if (!nik) return;

    // Check if already in the list
    const isDuplicate = participantRows.some((row, i) => i !== idx && row.employee === nik);
    if (isDuplicate) {
      setToast({ message: "Employee already added to this list", type: "error" });
      const a = [...participantRows];
      a[idx].employee = "";
      setParticipantRows(a);
      return;
    }

    if (!startDate || !endDate) {
      const a = [...participantRows];
      a[idx].employee = nik;
      setParticipantRows(a);
      return;
    }

    try {
      const res = await api.get(`/api/check-participant-conflict/?nik=${nik}&start_date=${startDate}&end_date=${endDate}${editingId ? `&exclude_id=${editingId}` : ''}`);
      if (res.data.conflict) {
        setToast({ message: res.data.message, type: "error" });
        const a = [...participantRows];
        a[idx].employee = "";
        setParticipantRows(a);
      } else {
        const a = [...participantRows];
        a[idx].employee = nik;
        setParticipantRows(a);
      }
    } catch (e) {
      console.warn("Conflict check failed", e);
      const a = [...participantRows];
      a[idx].employee = nik;
      setParticipantRows(a);
    }
  };

  // ================= UI FUNCTIONS =================
  const handleFilter = (e) => {
    e.preventDefault();
    setPage(1);
    fetchTrainings();
  };

  const handleSaveAll = async () => {
    try {
      if (!trainingCode || !courseCategory || !courseId || !pic || !vendorId) {
        setToast({ message: "Please complete all required fields!", type: "error" });
        return;
      }

      const payload = {
        training_code: trainingCode,
        training_type: trainingType,
        training_category: trainingCategory,
        course_category: courseCategory,
        course: courseId,
        training_title: trainingTitle,
        training_description: trainingDescription,
        pic: pic,
        vendor_id: vendorId,
        estimated_cost: estimatedCost,
        topic: topic,
        start_date: startDate,
        end_date: endDate,
        status: status,
        location: {
          city: locationCity,
          venue: venue,
          room: room,
          address: address
        },
        schedules: scheduleRows,
        participants: participantRows,
        evaluation: {
          enable_course_access: evaluation.courseAccess,
          enable_feedback: evaluation.feedback,
          enable_evaluations: evaluation.evaluationStage
        },
        costs: costRows.map(row => {
          return {
            ...row,
            cost_center: row.division || ""
          };
        }),
        cost_allocation_type: costAllocationType,
        documents: documentationRows
      };

      if (isEditMode) {
        await api.put(`/api/add-training/${editingId}/`, payload);
        setToast({ message: "Training updated successfully", type: "success" });
      } else {
        await api.post("/api/add-training/", payload);
        setToast({ message: "Training added successfully", type: "success" });
      }

      setShowModal(false);
      setShowEventModal(false);
      setPage(1);
      fetchTrainings();
      setIsEditMode(false);
      setEditingId(null);
    } catch (error) {
      console.error("Failed to save:", error.response?.data || error.message);
      const errorMsg = error.response?.data?.error || error.response?.data?.message || "Failed to add training";
      setToast({ message: errorMsg, type: "error" });
    }
  };

  const handleDeleteClick = () => {
    if (!isAdmin || !editingId) return;
    setShowDeleteConfirm(true);
  };

  const handleConfirmDelete = async () => {
    try {
      await api.delete(`/api/add-training/${editingId}/`);
      setToast({ message: "Training deleted successfully", type: "success" });
      setShowModal(false);
      setShowEventModal(false);
      setShowDeleteConfirm(false);
      setPage(1);
      fetchTrainings();
      setIsEditMode(false);
      setEditingId(null);
    } catch (e) {
      console.error("Failed to delete:", e);
      setToast({ message: "Failed to delete training", type: "error" });
      setShowDeleteConfirm(false);
    }
  };

  const handleEdit = async (id) => {
    if (!isAdmin) return;
    try {
      setLoading(true);
      const res = await api.get(`/api/add-training/${id}/`);
      const data = res.data;

      setIsEditMode(true);
      setEditingId(id);

      // Reset all states before population
      setTrainingCode("");
      setTrainingType("Inhouse Training");
      setTrainingCategory("Soft Skill");
      setCourseCategory("");
      setCourseId("");
      setTrainingTitle("");
      setTrainingDescription("");
      setPic("");
      setVendorId("");
      setEstimatedCost("");
      setTopic("");
      setStartDate("");
      setEndDate("");
      setStatus("Draft");
      setLocationCity("");
      setVenue("");
      setRoom("");
      setAddress("");
      setScheduleRows([{ date: "", start: "", end: "", material: "", instructor: "" }]);
      setParticipantRows([{ employee: "", attendance: "Present", l1: "", l2: "" }]);
      setEvaluation({ courseAccess: false, feedback: false, evaluationStage: false });
      setCostRows([{ division: "", currency: "IDR", room: "", training: "", sppd: "", status: "Unpaid" }]);
      setDocumentationRows([{ type: "Invoice", file_name: "", url: "https://drive.google.com/drive/folders/1oM-ijNHhANgh7EFZvzUG_smQJBq4G77d?usp=sharing", submitted_by: "" }]);
      setTrainingCode(data.training_code || "");
      setTrainingType(data.training_type || "Inhouse Training");
      setTrainingCategory(data.training_category || "Soft Skill");
      setCourseCategory(data.course_category || "");
      setCourseId(data.course || "");
      setTrainingTitle(data.training_title || "");
      setTrainingDescription(data.training_description || "");
      setPic(data.pic || "");
      setVendorId(data.vendor || "");
      setEstimatedCost(data.estimated_cost || "");

      if (data.latest_event) {
        const ev = data.latest_event;
        setTopic(ev.topic || "");
        setStartDate(ev.start_date || "");
        setEndDate(ev.end_date || "");
        setStatus(ev.status === 'completed' ? 'Completed' : ev.status === 'cancelled' ? 'Cancelled' : 'Draft');

        if (ev.location) {
          setLocationCity(ev.location.city || "");
          setVenue(ev.location.venue || "");
          setRoom(ev.location.room || "");
          setAddress(ev.location.address || "");
        }

        setScheduleRows(ev.schedules?.length ? ev.schedules.map(s => ({
          date: s.training_date,
          start: s.start_time,
          end: s.end_time,
          material: s.material_link,
          instructor: s.instructor_name
        })) : [{ date: "", start: "", end: "", material: "", instructor: "" }]);

        setParticipantRows(ev.participants?.length ? ev.participants.map(p => {
          let score2 = p.l2_score;
          if (score2 > 4) {
            if (score2 <= 25) score2 = 1;
            else if (score2 <= 50) score2 = 2;
            else if (score2 <= 75) score2 = 3;
            else score2 = 4;
          }
          return {
            employee: p.nik,
            attendance: p.attendance_status || "Present",
            l1: p.l1_score,
            l2: score2
          };
        }) : [{ employee: "", attendance: "Present", l1: "", l2: "" }]);

        setEvaluation({
          courseAccess: ev.enable_course_access || false,
          feedback: ev.enable_feedback || false,
          evaluationStage: ev.enable_evaluations || false
        });

        if (ev.costs?.length) {
          setCostRows(ev.costs.map(c => ({
            division: c.cost_center || "",
            currency: c.currency,
            room: c.room_cost,
            training: c.training_cost,
            sppd: c.sppd_cost,
            status: c.status_cost
          })));
          setCostAllocationType(ev.costs[0].cost_type || "Estimate Cost");
        }

        setDocumentationRows(ev.documents?.length ? ev.documents.map(d => ({
          type: d.document_type,
          file_name: d.file_name,
          url: d.file_url,
          submitted_by: d.uploaded_by
        })) : [{ type: "", file_name: "", url: "", submitted_by: "" }]);
      }

      setShowModal(true);
    } catch (e) {
      console.error("Failed to fetch detail:", e);
      alert("Failed to fetch training detail");
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    // Replaced by handleDeleteClick and handleConfirmDelete
  };

  const openAddModal = () => {
    if (!isAdmin) return;
    setIsEditMode(false);
    setEditingId(null);

    // Step 1 states
    setTrainingCode("");
    setTrainingType("");
    setTrainingCategory("");
    setCourseCategory("");
    setCourseId("");
    setTrainingTitle("");
    setTrainingDescription("");
    setPic("");
    setVendorId("");
    setEstimatedCost("");

    // Step 2 states
    setTopic("");
    setStartDate("");
    setEndDate("");
    setStatus("");
    setLocationCity("");
    setVenue("");
    setRoom("");
    setAddress("");
    setScheduleRows([{ date: "", start: "", end: "", material: "", instructor: "" }]);
    setParticipantRows([{ employee: "", attendance: "Present", l1: "", l2: "" }]);
    setEvaluation({ courseAccess: false, feedback: false, evaluationStage: false });
    setCostRows([]);
    setDocumentationRows([]);
    setCostAllocationType("Estimate Cost");
    setActiveTab("location");

    setShowModal(true);
  };

  const handleSaveBudget = async () => {
    try {
      if (!budgetName || !budgetStartDate || !budgetEndDate || !totalBudget) {
        setToast({ message: "Please fill all fields", type: "error" });
        return;
      }

      await api.post('/api/budgets/', {
        budget_name: budgetName,
        start_date_budget: budgetStartDate,
        end_date_budget: budgetEndDate,
        total_budget: totalBudget
      });

      setToast({ message: "Budget saved successfully", type: "success" });
      setShowBudgetModal(false);
      setBudgetName("");
      setBudgetStartDate("");
      setBudgetEndDate("");
      setTotalBudget("");
    } catch (err) {
      console.error("Failed to save budget", err);
      setToast({ message: "Failed to save budget", type: "error" });
    }
  };

  const handleExport = async (e, reportTypeOverride = null) => {
    if (e) e.preventDefault();

    let params = new URLSearchParams();
    let formData = null;
    if (e) {
      formData = new FormData(e.target);
      for (let [key, value] of formData.entries()) {
        if (value) params.append(key, value);
      }
    }

    const reportType = reportTypeOverride || activeReportTab;

    try {


      if (reportType === "employee") {
        const divisionFilter = formData ? formData.get('division') : "";
        const statusFilter = formData ? formData.get('status') : "";
        const categoryFilter = formData ? formData.get('category') : "";
        const startDate = formData ? formData.get('start_date') : "";
        const endDate = formData ? formData.get('end_date') : "";
        let yearFilter = "";
        if (startDate) {
          yearFilter = new Date(startDate).getFullYear().toString();
        } else {
          yearFilter = selectedYear;
        }

        const params = new URLSearchParams();
        params.append("nopage", "true");
        params.append("report", "true");
        if (divisionFilter) params.append("division", divisionFilter);
        if (statusFilter) params.append("status", statusFilter);
        if (categoryFilter) params.append("category", categoryFilter);
        if (startDate) params.append("start_date", startDate);
        if (endDate) params.append("end_date", endDate);
        if (yearFilter) params.append("year", yearFilter);

        setToast({ message: "Generating Employee Report...", type: "success" });
        const res = await api.get(`/api/employee/?${params.toString()}`);
        const dataToExport = res.data;

        if (!dataToExport || !dataToExport.length) {
          setToast({ message: "No data available to export.", type: "error" });
          return;
        }

        const wb = XLSX.utils.book_new();
        const header = [[
          'NIK', 'Nama', 'Division', 'Level', 'Position', 'Special Position',
          'Training Title', 'Training Category', 'Inhouse Training', 'Public Training',
          'Knowledge Sharing', 'E-Learning', 'Total Hours', 'Inhouse Tr. Hours',
          'Public Tr. Hours', 'KS Hours', 'E-Learning Hours', 'TNA', 'TNA Fulfilled'
        ]];

        const rows = [];
        const merges = [];
        let currentRow = 1;

        dataToExport.forEach(emp => {
          const details = emp.attendance_details || [];
          const numRows = details.length || 1;

          if (details.length === 0) {
            rows.push([
              emp.nik,
              emp.full_name,
              emp.division_name || '',
              emp.level || '',
              emp.position_name || '',
              emp.special_position || '-',
              '-',
              '-',
              0,
              0,
              0,
              0,
              emp.total_hours,
              emp.inhouse_hours,
              emp.public_hours,
              emp.ks_hours,
              emp.elearning_hours,
              '-',
              emp.tna_fulfilled > 0 ? emp.tna_fulfilled : '-'
            ]);
            currentRow++;
          } else {
            details.forEach((d, idx) => {
              const tType = d.type || "";
              rows.push([
                emp.nik,
                emp.full_name,
                emp.division_name || '',
                emp.level || '',
                emp.position_name || '',
                emp.special_position || '-',
                d.title || '-',
                d.category || '-',
                tType === 'Inhouse Training' ? 1 : 0,
                tType === 'Public Training' ? 1 : 0,
                tType === 'Knowledge Sharing' ? 1 : 0,
                tType === 'E-Learning' ? 1 : 0,
                emp.total_hours,
                emp.inhouse_hours,
                emp.public_hours,
                emp.ks_hours,
                emp.elearning_hours,
                d.tna || '-',
                emp.tna_fulfilled > 0 ? emp.tna_fulfilled : '-'
              ]);
            });

            if (numRows > 1) {
              for (let c = 0; c <= 5; c++) {
                merges.push({ s: { r: currentRow, c: c }, e: { r: currentRow + numRows - 1, c: c } });
              }
              for (let c = 12; c <= 16; c++) {
                merges.push({ s: { r: currentRow, c: c }, e: { r: currentRow + numRows - 1, c: c } });
              }
              merges.push({ s: { r: currentRow, c: 18 }, e: { r: currentRow + numRows - 1, c: 18 } });
            }
            currentRow += numRows;
          }
        });

        const ws = XLSX.utils.aoa_to_sheet([...header, ...rows]);
        ws['!merges'] = merges;
        ws['!cols'] = [
          { wch: 15 }, { wch: 30 }, { wch: 25 }, { wch: 10 }, { wch: 25 }, { wch: 20 },
          { wch: 45 }, { wch: 18 }, { wch: 18 }, { wch: 18 }, { wch: 18 }, { wch: 18 },
          { wch: 12 }, { wch: 18 }, { wch: 18 }, { wch: 15 }, { wch: 18 }, { wch: 25 }, { wch: 15 }
        ];

        XLSX.utils.book_append_sheet(wb, ws, "Employee Report");
        XLSX.writeFile(wb, `Employee_Report_${new Date().toISOString().split('T')[0]}.xlsx`);
        setToast({ message: "Employee Report exported successfully", type: "success" });
        setShowReportModal(false);
        return;
      }

      setToast({ message: "Generating Report...", type: "success" });
      const response = await api.get(`/api/export-report/?${params.toString()}`);
      const { realisasi_training, total_employees } = response.data;

      if (!realisasi_training || !realisasi_training.length) {
        setToast({ message: "No data found", type: "error" });
        return;
      }

      // ─── Case 1: Division Report (Merged Cells) ───────────────────────
      if (reportType === "division") {
        const divisionFilter = formData ? formData.get('division') : null;
        let targetEmployees = employees;
        if (divisionFilter && divisionFilter !== "") {
          targetEmployees = employees.filter(e => e.division_name === divisionFilter);
        }

        const empMap = {};
        targetEmployees.forEach(e => {
          const key = String(e.nik);
          empMap[key] = {
            nik: e.nik,
            nama: e.full_name,
            total_hours: 0,
            trainings: []
          };
        });

        realisasi_training.forEach(item => {
          const key = String(item.nik);
          if (empMap[key]) {
            empMap[key].total_hours += (Number(item.hours) || 0);
            empMap[key].trainings.push({
              title: item.training_title,
              hours: (Number(item.hours) || 0)
            });
          }
        });

        const wb = XLSX.utils.book_new();
        const header = [['NIK', 'Nama', 'Total Hours', 'Training Title']];
        const rows = [];
        const merges = [];
        let currentRow = 1;

        Object.values(empMap).forEach(emp => {
          const numRows = emp.trainings.length || 1;
          if (emp.trainings.length === 0) {
            rows.push([emp.nik, emp.nama, 0, '-']);
          } else {
            emp.trainings.forEach((t, idx) => {
              rows.push([emp.nik, emp.nama, emp.total_hours, t.title]);
            });
          }
          if (numRows > 1) {
            merges.push({ s: { r: currentRow, c: 0 }, e: { r: currentRow + numRows - 1, c: 0 } });
            merges.push({ s: { r: currentRow, c: 1 }, e: { r: currentRow + numRows - 1, c: 1 } });
            merges.push({ s: { r: currentRow, c: 2 }, e: { r: currentRow + numRows - 1, c: 2 } });
          }
          currentRow += numRows;
        });

        const ws = XLSX.utils.aoa_to_sheet([...header, ...rows]);
        ws['!merges'] = merges;
        ws['!cols'] = [{ wch: 12 }, { wch: 35 }, { wch: 15 }, { wch: 70 }];
        XLSX.utils.book_append_sheet(wb, ws, "Division Report");
        XLSX.writeFile(wb, `Division_Report_${new Date().toISOString().split('T')[0]}.xlsx`);
        setToast({ message: "Division Report exported successfully", type: "success" });
        setShowReportModal(false);
        return;
      }

      // ─── Case 3: Annual Report (Full dump sorted by date) ────────────
      if (reportType === "master") {
        const sortedData = [...realisasi_training].sort((a, b) => {
          const dA = a.start_date ? new Date(a.start_date) : new Date(0);
          const dB = b.start_date ? new Date(b.start_date) : new Date(0);
          return dA - dB;
        });

        const exportData = sortedData.map(item => {
          const row = {
            "Course Category": item.course_category,
            "Course Name": item.course_name,
            "Training Type": item.training_type,
            "Training Title": item.training_title,
            "Start Date": item.start_date,
            "End Date": item.end_date,
            "Days": item.duration_day,
            "Hours": item.hours,
            "Location": item.location,
            "Vendor": item.vendor,
            "Training Category": item.training_category,
            "NIK": item.nik,
            "Nama": item.nama,
            "Divisi": item.divisi,
            "Jabatan": item.jabatan,
          };
          if (!(user?.role === 'Head of Division' || user?.role === 'Employee')) {
            row["L1"] = item.l1;
            row["L2"] = item.l2;
            row["YearMonth"] = item.year_month;
            row["TNA Fulfillment"] = item.tna_fulfillment;
          }
          return row;
        });

        const ws = XLSX.utils.json_to_sheet(exportData);
        ws["!cols"] = [
          { wch: 20 }, { wch: 25 }, { wch: 18 }, { wch: 45 }, { wch: 12 },
          { wch: 12 }, { wch: 8 }, { wch: 8 }, { wch: 20 }, { wch: 25 },
          { wch: 18 }, { wch: 12 }, { wch: 30 }, { wch: 25 }, { wch: 25 }
        ];
        if (!(user?.role === 'Head of Division' || user?.role === 'Employee')) {
          ws["!cols"].push({ wch: 8 }, { wch: 8 }, { wch: 12 }, { wch: 15 });
        }

        const wb = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(wb, ws, "Annual Report");
        XLSX.writeFile(wb, `Annual_Report_${new Date().toISOString().split('T')[0]}.xlsx`);
        setToast({ message: "Annual Report exported successfully", type: "success" });
        setShowReportModal(false);
        return;
      }

      // ─── Case 2: Monthly Report (Existing 2-sheet logic) ───────────────
      if (reportType === "monthly") {
        console.log("Generating Monthly Report with", realisasi_training.length, "records");

        const slide1Data = realisasi_training.map(item => {
          const h = Number(item.hours) || 0;
          return {
            "Course Category": item.course_category || "",
            "Course Name": item.course_name || "",
            "Training Title": item.training_title || "",
            "Training Type": item.training_type || "",
            "Training Category": item.training_category || "",
            "Location": item.location || "",
            "Hours": h,
            "Start Date": item.start_date || "",
            "End Date": item.end_date || "",
            "Duration Day": item.duration_day || 0,
            "Vendor": item.vendor || "",
            "NIK": item.nik || "",
            "Nama": item.nama || "",
            "Divisi": item.divisi || "",
            "Level": item.level || "",
            "Jabatan": item.jabatan || "",
            "Direktorat": item.direktorat || "",
            "Gender": item.gender || ""
          };
        });

        const grandTotalHours = realisasi_training.reduce((sum, item) => sum + (Number(item.hours) || 0), 0);

        const wb = XLSX.utils.book_new();

        // Sheet 1: Realisasi Training
        const ws1 = XLSX.utils.json_to_sheet(slide1Data, { origin: "A3" });
        XLSX.utils.sheet_add_aoa(ws1, [
          ["Monthly Report", "", "Total Hours:", Number(grandTotalHours.toFixed(2))]
        ], { origin: "A1" });

        ws1["!cols"] = [
          { wch: 20 }, { wch: 25 }, { wch: 30 }, { wch: 20 }, { wch: 20 },
          { wch: 15 }, { wch: 10 }, { wch: 15 }, { wch: 15 }, { wch: 15 },
          { wch: 20 }, { wch: 15 }, { wch: 25 }, { wch: 20 }, { wch: 15 },
          { wch: 20 }, { wch: 20 }, { wch: 10 }
        ];
        XLSX.utils.book_append_sheet(wb, ws1, "Realisasi Training");

        // Sheet 2: Accumulation
        const monthlyData = {};
        realisasi_training.forEach(item => {
          if (!item.start_date) return;
          try {
            const d = new Date(item.start_date);
            if (isNaN(d.getTime())) return;
            const monthName = d.toLocaleString('default', { month: 'long' });
            const year = d.getFullYear();
            const key = `${monthName} ${year}`;
            
            if (!monthlyData[key]) {
              monthlyData[key] = {
                hours: 0,
                niks: new Set()
              };
            }
            monthlyData[key].hours += (Number(item.hours) || 0);
            if (item.nik) {
              monthlyData[key].niks.add(item.nik);
            }
          } catch (e) {
            console.warn("Date parsing error for item", item);
          }
        });

        const slide2AoA = [];
        const sortedMonthKeys = Object.keys(monthlyData).sort((a, b) => new Date(a) - new Date(b));

        if (sortedMonthKeys.length > 0) {
          sortedMonthKeys.forEach(key => {
            const monthlyHours = monthlyData[key].hours;
            const activeEmployees = monthlyData[key].niks.size;
            const avg = activeEmployees > 0 ? (monthlyHours / activeEmployees) : 0;
            
            slide2AoA.push([key, "Jumlah Jam Training", Number(monthlyHours.toFixed(2))]);
            slide2AoA.push(["", `Jumlah Karyawan per ${key}`, activeEmployees]);
            slide2AoA.push(["", "Rata-rata jam training", Number(avg.toFixed(2))]);
            slide2AoA.push([]);
          });
        } else {
          slide2AoA.push(["No data available for the selected period", "", ""]);
        }

        const ws2 = XLSX.utils.aoa_to_sheet(slide2AoA);
        ws2["!cols"] = [{ wch: 20 }, { wch: 35 }, { wch: 15 }];
        XLSX.utils.book_append_sheet(wb, ws2, "Akumulasi Jam Training");

        // Download
        const fileName = `Monthly_Report_${new Date().toISOString().split('T')[0]}.xlsx`;
        XLSX.writeFile(wb, fileName);

        setToast({ message: "Monthly Report exported successfully", type: "success" });
        setShowReportModal(false);
        return;
      }
    } catch (error) {
      console.error("Export failed:", error);
      setToast({ message: "Failed to generate report", type: "error" });
    }
  };

  return (
    <MainLayout>
      {isManagerialRole && (
        <div className="flex space-x-8 border-b border-gray-300 mb-6 px-4 sm:px-0 mt-4">
          <button
            onClick={() => setActiveView('admin')}
            className={`pb-3 px-1 font-bold text-xl transition-colors ${activeView === 'admin'
              ? 'text-[#2174C3] border-b-4 border-[#2174C3]'
              : 'text-gray-400 hover:text-[#2174C3]'
              }`}
          >
            {['Super Administrator', 'Administrator', 'Dean'].includes(user?.role) ? 'Company Training Master' : 'Division Training Master'}
          </button>
          <button
            onClick={() => setActiveView('employee')}
            className={`pb-3 px-1 font-bold text-xl transition-colors ${activeView === 'employee'
              ? 'text-[#2174C3] border-b-4 border-[#2174C3]'
              : 'text-gray-400 hover:text-[#2174C3]'
              }`}
          >
            My Training
          </button>
        </div>
      )}

      {/* ─── Toolbar ─────────────────────────────────────────────── */}
      <div className="bg-white p-3 rounded-xl shadow-sm border border-gray-100 flex flex-col sm:flex-row items-center gap-3 mb-10 transition-all hover:shadow-md sticky top-0 z-30">
        {/* Search */}
        <div className="relative w-full sm:w-1/3">
          <input
            type="text"
            placeholder="Search"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-4 pr-10 py-2 rounded-lg border-none bg-gray-100 focus:bg-white focus:ring-1 focus:ring-[#2174C3] transition-all text-gray-600 placeholder-gray-400"
          />
          <span className="absolute right-3 top-2.5 text-gray-400 pointer-events-none">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
            </svg>
          </span>
        </div>


        {/* Month Filter */}
        {activeView !== 'employee' && (
          <div className="relative w-full sm:w-48">
            <select
              value={month}
              onChange={(e) => setMonth(e.target.value)}
              className="w-full border-none rounded-lg pl-4 pr-10 py-2 text-sm text-gray-600 bg-gray-100 focus:bg-white focus:outline-none focus:ring-1 focus:ring-[#2174C3] appearance-none bg-no-repeat bg-right-4"
              style={{
                backgroundImage: `url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M19 9l-7 7-7-7'/%3e%3c/svg%3e")`,
                backgroundSize: '20px 20px',
                backgroundPosition: 'right 12px center'
              }}
            >
              <option value="">All Month</option>
              {["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"].map((m, idx) => (
                <option key={m} value={idx + 1}>{m}</option>
              ))}
            </select>
          </div>
        )}

        {/* Right Section: Year & Actions */}
        <div className="flex-1 flex justify-end items-center space-x-6 shrink-0">
          <YearPicker selectedYear={selectedYear} onYearChange={(y) => setSelectedYear(y)} />

          <div className="flex gap-2">
            <button
              onClick={() => {
                if (user?.role === 'Head of Division' || user?.role === 'Employee') {
                  handleExport(null, "master");
                } else {
                  setShowReportModal(true);
                }
              }}
              className="bg-[#2174C3] hover:bg-[#1A5E9D] text-white w-28 py-2 rounded-lg font-medium text-sm transition-all shadow-sm cursor-pointer"
            >
              Report
            </button>
            {isAdmin && user?.role !== 'Dean' && (
              <button
                onClick={openAddModal}
                className="bg-[#2174C3] hover:bg-[#1A5E9D] text-white w-28 py-1 rounded-lg font-medium flex items-center justify-center text-sm shadow-sm transition-all cursor-pointer"
              >
                <span className="mr-1 text-lg font-bold">+</span> Training
              </button>
            )}
          </div>
        </div>
      </div>

      <div className="flex justify-between items-center mb-8">
        <div className="flex items-center gap-4">
          <h1 className="text-4xl font-bold text-gray-800 tracking-tight">Training Master</h1>
        </div>
        {isAdmin && user?.role !== 'Dean' && (
          <button
            onClick={() => setShowBudgetModal(true)}
            className="bg-[#2174C3] hover:bg-[#1A5E9D] text-white w-28 py-1 rounded-lg font-medium flex items-center justify-center text-sm shadow-sm transition-all cursor-pointer"
          >
            <span className="mr-1 text-lg font-bold">+</span> Budget
          </button>
        )}
      </div>

      {/* ─── Table ───────────────────────────────────────────────── */}
      <div className="bg-white rounded-2xl shadow-xl border border-gray-100 overflow-hidden transition-all h-[calc(100vh-350px)] flex flex-col">
        <div className="custom-scrollbar overflow-auto flex-1">
          <table className="w-full text-left text-sm min-w-[2800px]">
            <thead className="bg-[#5C85BB] text-white text-xs uppercase tracking-wider sticky top-0 z-10">
              <tr>
                <th className="px-3 py-4 font-bold">Course Category</th>
                <th className="px-3 py-4 font-bold">Course Name</th>
                <th className="px-3 py-4 font-bold">Training Type</th>
                <th className="px-3 py-4 font-bold">Training Title</th>
                <th className="px-3 py-4 font-bold">Start Date</th>
                <th className="px-3 py-4 font-bold">End Date</th>
                <th className="px-3 py-4 font-bold text-center">Days</th>
                <th className="px-3 py-4 font-bold text-center">Hours</th>
                <th className="px-3 py-4 font-bold">Location</th>
                <th className="px-3 py-4 font-bold">Vendor</th>
                <th className="px-3 py-4 font-bold">Training Category</th>
                {((['Head of Division', 'Team Leader', 'Employee'].includes(user?.role)) || activeView === 'employee') && (
                  <th className="px-3 py-4 font-bold">Participants</th>
                )}
                {!((['Head of Division', 'Team Leader', 'Employee'].includes(user?.role)) || activeView === 'employee') && (
                  <>
                    <th className="px-3 py-4 font-bold text-center">L1</th>
                    <th className="px-3 py-4 font-bold text-center">L2</th>
                    <th className="px-3 py-4 font-bold text-right">Training Cost</th>
                    <th className="px-3 py-4 font-bold text-right">Venue Cost</th>
                    <th className="px-3 py-4 font-bold text-right">SPPD Cost</th>
                    <th className="px-3 py-4 font-bold text-right">Total Cost</th>
                  </>
                )}
              </tr>
            </thead>

            <tbody className="divide-y divide-gray-100">
              {loading ? (
                <tr>
                  <td colSpan="22" className="px-6 py-12 text-center text-gray-400">
                    <div className="flex items-center justify-center gap-2">
                      <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                      </svg>
                      Loading...
                    </div>
                  </td>
                </tr>
              ) : trainings.length === 0 ? (
                <tr>
                  <td colSpan="22" className="px-6 py-12 text-center text-gray-400">No data available</td>
                </tr>
              ) : (
                trainings.flatMap((t, i) => {
                  const isRestricted = ['Head of Division', 'Team Leader', 'Employee'].includes(user?.role) || activeView === 'employee';
                  const pNames = (t.division_participant_names || "").split(", ").filter(n => n);

                  if (isRestricted) {
                    // If restricted but somehow no names found (should not happen with backend filter)
                    if (pNames.length === 0) return [];

                    return pNames.map((name, pIdx) => (
                      <tr key={`${i}-${pIdx}`} className="hover:bg-blue-50/30 transition-colors cursor-pointer group border-b border-gray-50">
                        <td className="px-3 py-3 font-normal text-gray-700">{t.category_name}</td>
                        <td className="px-3 py-3 font-normal text-gray-700">{t.course_name}</td>
                        <td className="px-3 py-3 font-normal text-gray-700">{t.training_type}</td>
                        <td className="px-3 py-3 text-[#2174C3] font-normal hover:underline cursor-pointer" onClick={() => handleEdit(t.training_id)}>{t.training_title}</td>
                        <td className="px-3 py-3 font-normal text-gray-700">{t.start_date || "-"}</td>
                        <td className="px-3 py-3 font-normal text-gray-700">{t.end_date || "-"}</td>
                        <td className="px-3 py-3 text-center font-normal text-gray-700">{t.days}</td>
                        <td className="px-3 py-3 text-center font-normal text-gray-700">{t.hours}</td>
                        <td className="px-3 py-3 font-normal text-gray-700">{t.location}</td>
                        <td className="px-3 py-3 font-normal text-gray-700">{t.vendor_name}</td>
                        <td className="px-3 py-3 font-normal text-gray-700">
                          <span className={`px-2 py-0.5 rounded-full text-[9px] font-bold ${t.training_category === 'ESG' ? 'bg-green-100 text-green-700' :
                            t.training_category === 'Hard Skill' ? 'bg-orange-100 text-orange-700' : 'bg-blue-100 text-blue-700'
                            }`}>
                            {t.training_category}
                          </span>
                        </td>
                        <td className="px-3 py-3 font-normal text-gray-700 italic">{name}</td>
                      </tr>
                    ));
                  }

                  // Administrator / Full View
                  return (
                    <tr key={i} className="hover:bg-blue-50/30 transition-colors cursor-pointer group border-b border-gray-50">
                      <td className="px-3 py-3 font-normal text-gray-700">{t.category_name}</td>
                      <td className="px-3 py-3 font-normal text-gray-700">{t.course_name}</td>
                      <td className="px-3 py-3 font-normal text-gray-700">{t.training_type}</td>
                      <td className="px-3 py-3 text-[#2174C3] font-normal hover:underline cursor-pointer" onClick={() => handleEdit(t.training_id)}>{t.training_title}</td>
                      <td className="px-3 py-3 font-normal text-gray-700">{t.start_date || "-"}</td>
                      <td className="px-3 py-3 font-normal text-gray-700">{t.end_date || "-"}</td>
                      <td className="px-3 py-3 text-center font-normal text-gray-700">{t.days}</td>
                      <td className="px-3 py-3 text-center font-normal text-gray-700">{t.hours}</td>
                      <td className="px-3 py-3 font-normal text-gray-700">{t.location}</td>
                      <td className="px-3 py-3 font-normal text-gray-700">{t.vendor_name}</td>
                      <td className="px-3 py-3 font-normal text-gray-700">
                        <span className={`px-2 py-0.5 rounded-full text-[9px] font-bold ${t.training_category === 'ESG' ? 'bg-green-100 text-green-700' :
                          t.training_category === 'Hard Skill' ? 'bg-orange-100 text-orange-700' : 'bg-blue-100 text-blue-700'
                          }`}>
                          {t.training_category}
                        </span>
                      </td>
                      <td className="px-3 py-3 text-center font-normal text-gray-700">
                        {t.l1_avg ? Number(t.l1_avg).toFixed(2) : "0.00"}
                      </td>
                      <td className="px-3 py-3 text-center font-normal text-gray-700">
                        {t.l2_avg ? Number(t.l2_avg).toFixed(2) : "0.00"}
                      </td>
                      <td className="px-3 py-3 text-right font-normal text-gray-700">
                        {new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', maximumFractionDigits: 0 }).format(t.training_cost)}
                      </td>
                      <td className="px-3 py-3 text-right font-normal text-gray-700">
                        {new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', maximumFractionDigits: 0 }).format(t.venue_cost)}
                      </td>
                      <td className="px-3 py-3 text-right font-normal text-gray-700">
                        {new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', maximumFractionDigits: 0 }).format(t.sppd_cost)}
                      </td>
                      <td className="px-3 py-3 text-right font-bold text-gray-800 bg-gray-50/50">
                        {new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', maximumFractionDigits: 0 }).format(t.total_cost)}
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Pagination */}
      {totalPages > 1 ? (
        <div className="sticky bottom-0 bg-[#F4F7FA]/95 backdrop-blur-sm py-4 flex flex-col items-end gap-2 z-20 mt-4 border-t border-gray-100">
          <div className="flex items-center space-x-1">
            <button
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1}
              className="px-4 py-2 bg-[#E2E8F0] text-gray-500 rounded-md font-medium hover:bg-gray-300 transition-colors disabled:opacity-50"
            >
              Previous
            </button>
            {[...Array(totalPages)].map((_, i) => (
              <button
                key={i}
                onClick={() => setPage(i + 1)}
                className={`px-4 py-2 rounded-md font-medium transition-colors ${page === i + 1 ? 'bg-[#2174C3] text-white' : 'bg-white border border-gray-200 text-gray-700 hover:bg-gray-50'}`}
              >
                {i + 1}
              </button>
            ))}
            <button
              onClick={() => setPage(p => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
              className="px-4 py-2 bg-white border border-gray-200 text-gray-700 rounded-md font-medium hover:bg-gray-50 transition-colors disabled:opacity-50"
            >
              Next
            </button>
          </div>
          {!loading && totalCount > 0 && (
            <div className="text-right text-xs text-gray-400 font-medium">
              Showing {(page - 1) * 50 + 1}–{Math.min(page * 50, totalCount)} of {totalCount} training
            </div>
          )}
        </div>
      ) : (
        !loading && totalCount > 0 && (
          <div className="sticky bottom-0 bg-[#F4F7FA]/95 backdrop-blur-sm py-4 flex justify-end items-center z-20 mt-4 border-t border-gray-100">
            <div className="text-right text-xs text-gray-400 font-medium">
              Showing 1–{totalCount} of {totalCount} training
            </div>
          </div>
        )
      )}


      {/* ========================= MODAL REPORT ========================= */}
      {showReportModal && (
        <div className="fixed inset-0 flex items-center justify-center bg-black/60 z-[100] p-4">
          <div className="bg-white w-full max-w-2xl max-h-[90vh] overflow-y-auto rounded-xl shadow-2xl p-8 relative">
            <h2 className="text-3xl font-bold text-black mb-10">Report Form</h2>


            {/* Redesigned Tabs */}
            <div className="flex space-x-8 border-b border-gray-200 mb-8">
              {[
                { id: 'master', label: 'Annual Report' },
                { id: 'monthly', label: 'Monthly Report' },
                { id: 'division', label: 'Division Report' },
                { id: 'employee', label: 'Employee Report' }
              ].map((tab) => (
                <button
                  key={tab.id}
                  type="button"
                  onClick={() => setActiveReportTab(tab.id)}
                  className={`pb-3 px-1 font-bold text-sm tracking-wider transition-all relative ${activeReportTab === tab.id ? "text-[#2174C3]" : "text-gray-400 hover:text-gray-600"
                    }`}
                >
                  {tab.label}
                  {activeReportTab === tab.id && (
                    <div className="absolute bottom-0 left-0 right-0 h-1 bg-[#2174C3]" />
                  )}
                </button>
              ))}
            </div>

            <form onSubmit={handleExport} className="space-y-6">
              {/* Common Field: Training Date */}
              <div className="grid grid-cols-1 sm:grid-cols-3 items-center gap-2">
                <label className="text-black font-semibold">Training Date</label>
                <div className="sm:col-span-2 flex items-center gap-2">
                  <input type="date" name="start_date" className="flex-1 p-3 rounded-lg bg-gray-100 border-none focus:ring-2 focus:ring-[#2174C3] text-black" />
                  <span className="text-gray-400 font-medium">to</span>
                  <input type="date" name="end_date" className="flex-1 p-3 rounded-lg bg-gray-100 border-none focus:ring-2 focus:ring-[#2174C3] text-black" />
                </div>
              </div>

              {activeReportTab === "monthly" && (
                <>
                  <div className="grid grid-cols-1 sm:grid-cols-3 items-center gap-2">
                    <label className="text-black font-semibold">Training Event Status</label>
                    <select name="status" className="sm:col-span-2 p-3 rounded-lg bg-gray-100 border-none focus:ring-2 focus:ring-[#2174C3] text-black">
                      <option value="all">All Status</option>
                      <option value="Draft">Draft</option>
                      <option value="Completed">Completed</option>
                    </select>
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-3 items-center gap-2">
                    <label className="text-black font-semibold">Training Category</label>
                    <select name="category" className="sm:col-span-2 p-3 rounded-lg bg-gray-100 border-none focus:ring-2 focus:ring-[#2174C3] text-black">
                      <option value="all">All Category</option>
                      <option value="Hard Skill">Hard Skill</option>
                      <option value="Soft Skill">Soft Skill</option>
                      <option value="ESG">ESG</option>
                    </select>
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-3 items-center gap-2">
                    <label className="text-black font-semibold">Employee</label>
                    <select name="employee" className="sm:col-span-2 p-3 rounded-lg bg-gray-100 border-none focus:ring-2 focus:ring-[#2174C3] text-black">
                      <option value="">All Employee</option>
                      {employees.map((emp, i) => (
                        <option key={i} value={emp.nik}>{emp.full_name} ({emp.nik})</option>
                      ))}
                    </select>
                  </div>
                </>
              )}

              {activeReportTab === "division" && (
                <>
                  <div className="grid grid-cols-1 sm:grid-cols-3 items-center gap-2">
                    <label className="text-black font-semibold">Training Event Status</label>
                    <select name="status" className="sm:col-span-2 p-3 rounded-lg bg-gray-100 border-none focus:ring-2 focus:ring-[#2174C3] text-black">
                      <option value="all">All Status</option>
                      <option value="Draft">Draft</option>
                      <option value="Completed">Completed</option>
                    </select>
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-3 items-center gap-2">
                    <label className="text-black font-semibold">Training Category</label>
                    <select name="category" className="sm:col-span-2 p-3 rounded-lg bg-gray-100 border-none focus:ring-2 focus:ring-[#2174C3] text-black">
                      <option value="all">All Category</option>
                      <option value="Hard Skill">Hard Skill</option>
                      <option value="Soft Skill">Soft Skill</option>
                      <option value="ESG">ESG</option>
                    </select>
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-3 items-center gap-2">
                    <label className="text-black font-semibold">Division</label>
                    <select name="division" className="sm:col-span-2 p-3 rounded-lg bg-gray-100 border-none focus:ring-2 focus:ring-[#2174C3] text-black">
                      <option value="">All Division</option>
                      {divisions.map((d, i) => (
                        <option key={i} value={d.division_name}>{d.division_name}</option>
                      ))}
                    </select>
                  </div>
                </>
              )}

              {activeReportTab === "master" && (
                <>
                  <div className="grid grid-cols-1 sm:grid-cols-3 items-center gap-2">
                    <label className="text-black font-semibold">Training Event Status</label>
                    <select name="status" className="sm:col-span-2 p-3 rounded-lg bg-gray-100 border-none focus:ring-2 focus:ring-[#2174C3] text-black">
                      <option value="all">All Status</option>
                      <option value="Draft">Draft</option>
                      <option value="Completed">Completed</option>
                    </select>
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-3 items-center gap-2">
                    <label className="text-black font-semibold">Training Type</label>
                    <select name="type" className="sm:col-span-2 p-3 rounded-lg bg-gray-100 border-none focus:ring-2 focus:ring-[#2174C3] text-black">
                      <option value="all">All Type</option>
                      <option value="Inhouse Training">Inhouse Training</option>
                      <option value="Public Training">Public Training</option>
                      <option value="E-Learning">E-Learning</option>
                      <option value="Knowledge Sharing">Knowledge Sharing</option>
                    </select>
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-3 items-center gap-2">
                    <label className="text-black font-semibold">Training Category</label>
                    <select name="category" className="sm:col-span-2 p-3 rounded-lg bg-gray-100 border-none focus:ring-2 focus:ring-[#2174C3] text-black">
                      <option value="all">All Category</option>
                      <option value="Hard Skill">Hard Skill</option>
                      <option value="Soft Skill">Soft Skill</option>
                      <option value="ESG">ESG</option>
                    </select>
                  </div>
                </>
              )}



              {activeReportTab === "employee" && (
                <>
                  <div className="grid grid-cols-1 sm:grid-cols-3 items-center gap-2">
                    <label className="text-black font-semibold">Training Event Status</label>
                    <select name="status" className="sm:col-span-2 p-3 rounded-lg bg-gray-100 border-none focus:ring-2 focus:ring-[#2174C3] text-black">
                      <option value="all">All Status</option>
                      <option value="Draft">Draft</option>
                      <option value="Completed">Completed</option>
                    </select>
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-3 items-center gap-2">
                    <label className="text-black font-semibold">Training Category</label>
                    <select name="category" className="sm:col-span-2 p-3 rounded-lg bg-gray-100 border-none focus:ring-2 focus:ring-[#2174C3] text-black">
                      <option value="all">All Category</option>
                      <option value="Hard Skill">Hard Skill</option>
                      <option value="Soft Skill">Soft Skill</option>
                      <option value="ESG">ESG</option>
                    </select>
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-3 items-center gap-2">
                    <label className="text-black font-semibold">Division</label>
                    <select name="division" className="sm:col-span-2 p-3 rounded-lg bg-gray-100 border-none focus:ring-2 focus:ring-[#2174C3] text-black">
                      <option value="">All Division</option>
                      {divisions.map((d, i) => (
                        <option key={i} value={d.division_name}>{d.division_name}</option>
                      ))}
                    </select>
                  </div>
                </>
              )}

              <div className="flex justify-end gap-3 mt-10">
                <button
                  type="button"
                  onClick={() => setShowReportModal(false)}
                  className="bg-[#878D94] hover:bg-[#607D8B] text-white px-4 py-1.5 text-sm rounded font-medium transition-colors cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="bg-[#2174C3] hover:bg-[#1A5E9D] text-white px-4 py-1.5 text-sm rounded font-medium transition-colors shadow-sm cursor-pointer"
                >
                  Export
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ========================= MODAL ADD TRAINING (STEP 1) ========================= */}
      {showModal && (
        <div className="fixed inset-0 flex items-center justify-center bg-black/60 z-[100] p-4">
          <div className="bg-white w-full max-w-2xl max-h-[90vh] overflow-y-auto custom-scrollbar rounded-xl shadow-2xl p-8 relative">
            <h2 className="text-3xl font-bold text-black mb-2">{isEditMode ? "Edit Training" : "Add Training"}</h2>
            <p className="text-sm text-gray-400 mb-6">Step 1: Training Information</p>
            <hr className="mb-8 border-gray-200" />

            <div className="space-y-6">
              <div className="grid grid-cols-1 sm:grid-cols-3 items-center gap-2">
                <label className="text-black font-semibold">Training Code</label>
                <input type="text" value={trainingCode} style={{ color: '#000' }}
                  onChange={(e) => setTrainingCode(e.target.value)}
                  onBlur={(e) => checkTrainingCode(e.target.value)}
                  className="sm:col-span-2 p-3 rounded-lg bg-gray-100 border-none focus:ring-2 focus:ring-[#2174C3]" placeholder="Enter training code e.g. LDPB1-26" />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 items-center gap-2">
                <label className="text-black font-semibold">Training Type</label>
                <select className="sm:col-span-2 p-3 rounded-lg bg-gray-100 border-none focus:ring-2 focus:ring-[#2174C3] text-black" value={trainingType} onChange={(e) => setTrainingType(e.target.value)}>
                  <option value="">Select Type</option>
                  <option value="Inhouse Training">Inhouse Training</option>
                  <option value="Public Training">Public Training</option>
                  <option value="E-Learning">E-Learning</option>
                  <option value="Knowledge Sharing">Knowledge Sharing</option>
                </select>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 items-center gap-2">
                <label className="text-black font-semibold">Category</label>
                <select className="sm:col-span-2 p-3 rounded-lg bg-gray-100 border-none focus:ring-2 focus:ring-[#2174C3] text-black" value={trainingCategory} onChange={(e) => setTrainingCategory(e.target.value)}>
                  <option value="">Select Category</option>
                  <option value="Hard Skill">Hard Skill</option>
                  <option value="Soft Skill">Soft Skill</option>
                  <option value="ESG">ESG</option>
                </select>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 items-center gap-2">
                <label className="text-black font-semibold">Course Category</label>
                <select className="sm:col-span-2 p-3 rounded-lg bg-gray-100 border-none focus:ring-2 focus:ring-[#2174C3] text-black" value={courseCategory} onChange={(e) => setCourseCategory(e.target.value)}>
                  <option value="">Select Course Category</option>
                  {courseCategories.map((c, i) => (
                    <option key={i} value={c.course_category_id}>{c.category_name}</option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 items-center gap-2">
                <label className="text-black font-semibold">Course</label>
                <select className="sm:col-span-2 p-3 rounded-lg bg-gray-100 border-none focus:ring-2 focus:ring-[#2174C3] text-black" value={courseId} onChange={(e) => setCourseId(e.target.value)}>
                  <option value="">Select Course</option>
                  {courses.map((c, i) => (
                    <option key={i} value={c.course_id}>{c.course_name}</option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 items-center gap-2">
                <label className="text-black font-semibold">Training Title</label>
                <input type="text" className="sm:col-span-2 p-3 rounded-lg bg-gray-100 border-none focus:ring-2 focus:ring-[#2174C3]" style={{ color: '#000' }} value={trainingTitle} onChange={(e) => setTrainingTitle(e.target.value)} placeholder="Enter training title" />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 items-start gap-2">
                <label className="text-black font-semibold pt-2">Description</label>
                <textarea rows="3" className="sm:col-span-2 p-3 rounded-lg bg-gray-100 border-none focus:ring-2 focus:ring-[#2174C3]" style={{ color: '#000' }} value={trainingDescription} onChange={(e) => setTrainingDescription(e.target.value)} placeholder="Enter training description, background and objective"></textarea>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 items-center gap-2">
                <label className="text-black font-semibold">PIC</label>
                <select className="sm:col-span-2 p-3 rounded-lg bg-gray-100 border-none focus:ring-2 focus:ring-[#2174C3] text-black" value={pic} onChange={(e) => setPic(e.target.value)}>
                  <option value="">Select PIC</option>
                  {employees
                    .filter(emp => [200335, 200331, 200329].includes(Number(emp.nik)))
                    .map((emp, i) => (
                      <option key={i} value={emp.nik}>{emp.full_name}</option>
                    ))}
                </select>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 items-center gap-2">
                <label className="text-black font-semibold">Vendor</label>
                <select className="sm:col-span-2 p-3 rounded-lg bg-gray-100 border-none focus:ring-2 focus:ring-[#2174C3] text-black" value={vendorId} onChange={(e) => setVendorId(e.target.value)}>
                  <option value="">Select Vendor</option>
                  {vendors.map((v, i) => (
                    <option key={i} value={v.vendor_id}>{v.vendor_name}</option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 items-center gap-2">
                <label className="text-black font-semibold">Estimated Cost</label>
                <div className="sm:col-span-2 relative">
                  <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 font-bold">IDR</span>
                  <input type="number" className="w-full pl-12 pr-4 py-3 rounded-lg bg-gray-100 border-none focus:ring-2 focus:ring-[#2174C3]" style={{ color: '#000' }} value={estimatedCost} onChange={(e) => setEstimatedCost(e.target.value)} />
                </div>
              </div>
            </div>

            <div className="flex justify-end space-x-2 mt-10">
              {isEditMode && user?.role !== 'Dean' && (
                <button type="button" onClick={handleDeleteClick} className="bg-red-500 hover:bg-red-600 text-white px-3 py-1 text-sm rounded font-medium transition-colors cursor-pointer">Delete</button>
              )}
              <button type="button" onClick={() => { setShowModal(false); setIsEditMode(false); setEditingId(null); }} className="bg-[#878D94] hover:bg-[#607D8B] text-white px-3 py-1 text-sm rounded font-medium transition-colors cursor-pointer">Cancel</button>
              <button type="button" onClick={() => { setShowModal(false); setShowEventModal(true); }} className="bg-[#2174C3] hover:bg-[#1A5E9D] text-white px-4 py-1 text-sm rounded font-medium transition-colors shadow cursor-pointer">Next</button>
            </div>
          </div>
        </div>
      )}

      {/* ========================= MODAL TRAINING EVENT (STEP 2) ========================= */}
      {showEventModal && (
        <div className="fixed inset-0 flex items-center justify-center bg-black/60 z-[110] p-4">
          <div className="bg-white w-full max-w-4xl max-h-[95vh] overflow-y-auto custom-scrollbar rounded-xl shadow-2xl p-10 relative">
            <h2 className="text-3xl font-bold text-black mb-2">{isEditMode ? "Edit Event Training" : "Event Training"}</h2>
            <p className="text-sm text-gray-400 mb-6">Step 2: Event Training Information</p>
            <hr className="mb-8 border-gray-200" />

            <div className="space-y-6 mb-10">
              {/* Training Topic */}
              <div className="grid grid-cols-1 sm:grid-cols-3 items-center gap-2">
                <label className="text-black font-semibold">Training Topic</label>
                <input type="text" className="sm:col-span-2 p-3 rounded-lg bg-gray-100 border-none focus:ring-2 focus:ring-[#2174C3] text-black" value={topic} onChange={(e) => setTopic(e.target.value)} placeholder="Enter training topic" />
              </div>

              {/* Start & End Date */}
              <div className="grid grid-cols-1 sm:grid-cols-3 items-center gap-2">
                <label className="text-black font-semibold">Start Date</label>
                <div className="sm:col-span-2 flex items-center gap-4">
                  <input type="date" className="flex-1 p-3 rounded-lg bg-gray-100 border-none focus:ring-2 focus:ring-[#2174C3] text-black" value={startDate} onChange={(e) => setStartDate(e.target.value)} />
                  <label className="text-black font-semibold shrink-0">End Date</label>
                  <input type="date" className="flex-1 p-3 rounded-lg bg-gray-100 border-none focus:ring-2 focus:ring-[#2174C3] text-black" value={endDate} onChange={(e) => setEndDate(e.target.value)} />
                </div>
              </div>

              {/* Event Status */}
              <div className="grid grid-cols-1 sm:grid-cols-3 items-center gap-2">
                <label className="text-black font-semibold">Training Status</label>
                <select className="sm:col-span-2 p-3 rounded-lg bg-gray-100 border-none focus:ring-2 focus:ring-[#2174C3] text-black" value={status} onChange={(e) => setStatus(e.target.value)}>
                  <option value="">Select Status</option>
                  <option value="Draft">Draft</option>
                  <option value="Completed">Completed</option>
                  <option value="Cancelled">Cancelled</option>
                </select>
              </div>
            </div>

            {/* Sub-Tabs */}
            <div className="flex gap-8 border-b border-gray-100 mb-6 overflow-x-auto whitespace-nowrap scrollbar-hide">
              {['Location', 'Schedule', 'Participant', 'Evaluation', 'Cost Management', 'Documentation'].map((tab) => {
                const tabKey = tab.toLowerCase().split(' ')[0];
                const displayTab = tab;
                return (
                  <button
                    key={tab}
                    type="button"
                    onClick={() => setActiveTab(tabKey === 'cost' ? 'cost' : tabKey === 'documentation' ? 'doc' : tabKey)}
                    className={`pb-4 px-1 font-bold text-sm transition-all relative ${(activeTab === tabKey || (activeTab === 'doc' && tabKey === 'documentation') || (activeTab === 'cost' && tabKey === 'cost'))
                      ? "text-[#2174C3]"
                      : "text-gray-400 hover:text-gray-600"
                      }`}
                  >
                    {displayTab}
                    {(activeTab === tabKey || (activeTab === 'doc' && tabKey === 'documentation') || (activeTab === 'cost' && tabKey === 'cost')) && (
                      <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-[#2174C3]" />
                    )}
                  </button>
                );
              })}
            </div>

            {/* TAB CONTENTS */}
            <div className="min-h-[300px]">
              {activeTab === "location" && (
                <div className="space-y-6">
                  <h3 className="text-[#2174C3] font-bold text-lg mb-4">Location</h3>
                  <div className="grid grid-cols-1 sm:grid-cols-3 items-center gap-2">
                    <label className="text-black font-semibold">Location City</label>
                    <input type="text" className="sm:col-span-2 p-3 rounded-lg bg-gray-100 border-none focus:ring-2 focus:ring-[#2174C3] text-black" value={locationCity} onChange={(e) => setLocationCity(e.target.value)} placeholder="Enter location city" />
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-3 items-center gap-2">
                    <label className="text-black font-semibold">Venue</label>
                    <input type="text" className="sm:col-span-2 p-3 rounded-lg bg-gray-100 border-none focus:ring-2 focus:ring-[#2174C3] text-black" value={venue} onChange={(e) => setVenue(e.target.value)} placeholder="Enter location venue" />
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-3 items-center gap-2">
                    <label className="text-black font-semibold">Room</label>
                    <input type="text" className="sm:col-span-2 p-3 rounded-lg bg-gray-100 border-none focus:ring-2 focus:ring-[#2174C3] text-black" value={room} onChange={(e) => setRoom(e.target.value)} placeholder="Enter location room" />
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-3 items-start gap-2">
                    <label className="text-black font-semibold pt-2">Address</label>
                    <textarea className="sm:col-span-2 p-3 rounded-lg bg-gray-100 border-none focus:ring-2 focus:ring-[#2174C3] text-black" rows="4" value={address} onChange={(e) => setAddress(e.target.value)} placeholder="Enter location address"></textarea>
                  </div>
                </div>
              )}

              {activeTab === "schedule" && (
                <div className="space-y-4">
                  <h3 className="text-[#2174C3] font-bold text-lg mb-4">Schedule</h3>
                  <div className="custom-scrollbar overflow-auto border border-gray-100 rounded-lg">
                    <table className="w-full text-sm">
                      <thead className="bg-gray-50 text-gray-500 text-[10px] uppercase font-bold text-center border-b border-gray-100">
                        <tr>
                          <th className="p-3 w-[50px]"></th>
                          <th className="p-3">Date</th>
                          <th className="p-3">Start Time</th>
                          <th className="p-3">End Time</th>
                          <th className="p-3">Material</th>
                          <th className="p-3">Instructor</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-100">
                        {scheduleRows.map((row, idx) => (
                          <tr key={idx}>
                            <td className="p-2">
                              <button type="button" onClick={() => setScheduleRows(prev => prev.filter((_, i) => i !== idx))} className="w-6 h-6 rounded-full bg-red-50 text-red-500 text-xs font-bold">×</button>
                            </td>
                            <td className="p-2"><input type="date" value={row.date} onChange={(e) => { const a = [...scheduleRows]; a[idx].date = e.target.value; setScheduleRows(a); }} className="w-full p-2 bg-gray-50 rounded" /></td>
                            <td className="p-2"><input type="text" placeholder="00:00" maxLength="5" value={row.start} onChange={(e) => { const a = [...scheduleRows]; a[idx].start = e.target.value; setScheduleRows(a); }} className="w-full p-2 bg-gray-50 rounded text-center font-mono" /></td>
                            <td className="p-2"><input type="text" placeholder="00:00" maxLength="5" value={row.end} onChange={(e) => { const a = [...scheduleRows]; a[idx].end = e.target.value; setScheduleRows(a); }} className="w-full p-2 bg-gray-50 rounded text-center font-mono" /></td>
                            <td className="p-2"><input type="text" value={row.material} onChange={(e) => { const a = [...scheduleRows]; a[idx].material = e.target.value; setScheduleRows(a); }} className="w-full bg-gray-100 rounded-lg p-3 border-none focus:ring-2 focus:ring-[#2174C3] text-sm text-black" placeholder="Enter material" /></td>
                            <td className="p-2"><input type="text" value={row.instructor} onChange={(e) => { const a = [...scheduleRows]; a[idx].instructor = e.target.value; setScheduleRows(a); }} className="w-full bg-gray-100 rounded-lg p-3 border-none focus:ring-2 focus:ring-[#2174C3] text-sm text-black" placeholder="Enter instructor" /></td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                  <button type="button" onClick={() => setScheduleRows([...scheduleRows, { date: "", start: "", end: "", material: "", instructor: "" }])} className="text-[#2174C3] font-bold text-sm">+ Add Schedule</button>
                </div>
              )}

              {activeTab === "participant" && (
                <div className="space-y-4">
                  <h3 className="text-[#2174C3] font-bold text-lg mb-4">Participant</h3>
                  <div className="custom-scrollbar overflow-visible border border-gray-100 rounded-lg">
                    <table className="w-full text-sm min-w-[600px] relative">
                      <thead className="bg-gray-50 text-gray-500 text-[10px] uppercase font-bold text-center border-b border-gray-100">
                        <tr>
                          <th className="p-3 w-[50px]"></th>
                          <th className="p-3">Employee Name</th>
                          <th className="p-3 w-[200px]">Attendance Status</th>
                          <th className="p-3 w-[120px]">L1 Score</th>
                          <th className="p-3 w-[120px]">L2 Score</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-100">
                        {participantRows.map((row, idx) => (
                          <tr key={idx}>
                            <td className="p-2">
                              <button type="button" onClick={() => setParticipantRows(prev => prev.filter((_, i) => i !== idx))} className="w-6 h-6 rounded-full bg-red-50 text-red-500 text-xs font-bold">×</button>
                            </td>
                            <td className="p-2">
                              <select
                                value={row.employee}
                                onChange={(e) => handleEmployeeChange(idx, e.target.value)}
                                className="w-full bg-gray-100 rounded-lg p-3 border-none focus:ring-2 focus:ring-[#2174C3] text-sm text-black"
                              >
                                <option value="">Select Employee</option>
                                {employees.map((emp, i) => (
                                  <option key={i} value={emp.nik}>({emp.nik}) {emp.full_name}</option>
                                ))}
                              </select>
                            </td>
                            <td className="p-2">
                              <select
                                value={row.attendance}
                                onChange={(e) => { const a = [...participantRows]; a[idx].attendance = e.target.value; setParticipantRows(a); }}
                                className="w-full bg-gray-100 rounded-lg p-3 border-none focus:ring-2 focus:ring-[#2174C3] text-sm text-black"
                              >
                                <option value="Present">Present</option>
                                <option value="Absent">Absent</option>
                              </select>
                            </td>
                            <td className="p-2"><input type="number" step="0.1" max="4" placeholder="1-4" value={row.l1} onChange={(e) => { const val = e.target.value; const a = [...participantRows]; a[idx].l1 = (val > 4) ? 4 : val; setParticipantRows(a); }} className="w-full bg-gray-100 rounded-lg p-3 border-none focus:ring-2 focus:ring-[#2174C3] text-sm text-black" /></td>
                            <td className="p-2"><input type="number" step="0.1" max="4" placeholder="1-4" value={row.l2} onChange={(e) => { const val = e.target.value; const a = [...participantRows]; a[idx].l2 = (val > 4) ? 4 : val; setParticipantRows(a); }} className="w-full bg-gray-100 rounded-lg p-3 border-none focus:ring-2 focus:ring-[#2174C3] text-sm text-black" /></td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                  <button type="button" onClick={() => setParticipantRows([...participantRows, { employee: "", attendance: "Present", l1: "", l2: "" }])} className="text-[#2174C3] font-bold text-sm">+ Add Participant</button>
                </div>
              )}

              {activeTab === "evaluation" && (
                <div className="space-y-8">
                  <h3 className="text-[#2174C3] font-bold text-lg mb-6">Evaluation</h3>

                  <div className="space-y-6">
                    <div className="flex items-center space-x-12">
                      <div className="flex items-center w-72 justify-between">
                        <label className="text-gray-700 font-semibold">Enable Training Access</label>
                        <input
                          type="checkbox"
                          checked={evaluation.courseAccess}
                          onChange={(e) => setEvaluation({ ...evaluation, courseAccess: e.target.checked })}
                          className="w-5 h-5 rounded border-gray-300 text-[#2174C3] focus:ring-[#2174C3] cursor-pointer"
                        />
                      </div>
                      <span className="text-red-500 text-sm font-medium">Content has not been configured</span>
                    </div>

                    <div className="flex items-center space-x-12">
                      <div className="flex items-center w-72 justify-between">
                        <label className="text-gray-700 font-semibold">Enable Feedback (L1 Templates)</label>
                        <input
                          type="checkbox"
                          checked={evaluation.feedback}
                          onChange={(e) => setEvaluation({ ...evaluation, feedback: e.target.checked })}
                          className="w-5 h-5 rounded border-gray-300 text-[#2174C3] focus:ring-[#2174C3] cursor-pointer"
                        />
                      </div>
                      <span className="text-red-500 text-sm font-medium">Feedback has not been configured</span>
                    </div>

                    <div className="flex items-center space-x-12">
                      <div className="flex items-center w-72 justify-between">
                        <label className="text-gray-700 font-semibold">Enable Evaluation (L2 Templates)</label>
                        <input
                          type="checkbox"
                          checked={evaluation.evaluationStage}
                          onChange={(e) => setEvaluation({ ...evaluation, evaluationStage: e.target.checked })}
                          className="w-5 h-5 rounded border-gray-300 text-[#2174C3] focus:ring-[#2174C3] cursor-pointer"
                        />
                      </div>
                      <span className="text-red-500 text-sm font-medium">Evaluation Stage has not been configured</span>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === "cost" && (
                <div className="space-y-6">
                  <h3 className="text-[#2174C3] font-bold text-lg mb-4">Cost Management</h3>
                  <div className="flex items-center space-x-4 mb-2">
                    <span className="text-[#333] font-bold text-sm">Training Cost Allocation Type</span>
                    <div className="relative">
                      <select
                        value={costAllocationType}
                        onChange={(e) => setCostAllocationType(e.target.value)}
                        className="bg-[#F3F4F6] border-none rounded-lg py-2 px-4 pr-10 text-sm font-bold appearance-none focus:ring-2 focus:ring-[#2174C3] cursor-pointer text-black"
                      >
                        <option value="Actual Cost" style={{ color: '#000' }}>Actual Cost</option>
                        <option value="Estimate Cost" style={{ color: '#000' }}>Estimate Cost</option>
                      </select>
                      <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none">
                        <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path>
                        </svg>
                      </div>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <div className="custom-scrollbar overflow-auto border border-gray-100 rounded-lg">
                      <table className="w-full text-sm min-w-[800px]">
                        <thead className="bg-gray-50 text-gray-500 text-[10px] uppercase font-bold text-center border-b border-gray-100">
                          <tr>
                            <th className="p-3 w-[50px]"></th>
                            <th className="p-3">Cost Center</th>
                            <th className="p-3 w-[100px]">Currency</th>
                            <th className="p-3">Training Cost</th>
                            <th className="p-3">Venue Cost</th>
                            <th className="p-3">SPPD Cost</th>
                            <th className="p-3 w-[120px]">Status</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-100">
                          {costRows.map((row, idx) => {
                            const selectedDivObj = divisions.find(d => parseInt(d.division_id) === parseInt(row.division));
                            const abbr = selectedDivObj ? getAbbreviation(selectedDivObj.division_name) : "";

                            return (
                              <tr key={idx}>
                                <td className="p-2">
                                  <button type="button" onClick={() => setCostRows(prev => prev.filter((_, i) => i !== idx))} className="w-6 h-6 rounded-full bg-red-50 text-red-500 text-xs font-bold">×</button>
                                </td>
                                <td className="p-2">
                                  <div className="space-y-1">
                                    <select
                                      value={row.division}
                                      onChange={(e) => { const a = [...costRows]; a[idx].division = e.target.value; setCostRows(a); }}
                                      className="w-full bg-gray-100 rounded-lg p-3 border-none focus:ring-2 focus:ring-[#2174C3] text-sm text-black"
                                    >
                                      <option value="">Select Division</option>
                                      {divisions.map(div => (
                                        <option key={div.division_id} value={div.division_id}>{div.division_name}</option>
                                      ))}
                                    </select>
                                    {abbr && <span className="text-[10px] text-gray-500 font-bold ml-2">Code: {abbr}</span>}
                                  </div>
                                </td>
                                <td className="p-2">
                                  <select
                                    value={row.currency}
                                    onChange={(e) => { const a = [...costRows]; a[idx].currency = e.target.value; setCostRows(a); }}
                                    className="w-full bg-gray-100 rounded-lg p-3 border-none focus:ring-2 focus:ring-[#2174C3] text-sm text-black"
                                  >
                                    <option value="IDR">IDR</option>
                                  </select>
                                </td>
                                <td className="p-2"><input type="number" placeholder="Enter cost" value={row.training} onChange={(e) => { const a = [...costRows]; a[idx].training = e.target.value; setCostRows(a); }} className="w-full bg-gray-100 rounded-lg p-3 border-none focus:ring-2 focus:ring-[#2174C3] text-sm text-black" /></td>
                                <td className="p-2"><input type="number" placeholder="Enter cost" value={row.room} onChange={(e) => { const a = [...costRows]; a[idx].room = e.target.value; setCostRows(a); }} className="w-full bg-gray-100 rounded-lg p-3 border-none focus:ring-2 focus:ring-[#2174C3] text-sm text-black" /></td>
                                <td className="p-2"><input type="number" placeholder="Enter cost" value={row.sppd} onChange={(e) => { const a = [...costRows]; a[idx].sppd = e.target.value; setCostRows(a); }} className="w-full bg-gray-100 rounded-lg p-3 border-none focus:ring-2 focus:ring-[#2174C3] text-sm text-black" /></td>
                                <td className="p-2">
                                  <select
                                    value={row.status}
                                    onChange={(e) => { const a = [...costRows]; a[idx].status = e.target.value; setCostRows(a); }}
                                    className="w-full bg-gray-100 rounded-lg p-3 border-none focus:ring-2 focus:ring-[#2174C3] text-sm text-black"
                                  >
                                    <option value="">Status</option>
                                    <option value="Unpaid">Unpaid</option>
                                    <option value="Paid">Paid</option>
                                  </select>
                                </td>
                              </tr>
                            );
                          })}
                        </tbody>
                      </table>
                    </div>
                    <button type="button" onClick={() => setCostRows([...costRows, { division: "", currency: "IDR", room: "", training: "", sppd: "", status: "" }])} className="text-[#2174C3] font-bold text-sm">+ Add Cost Center Allocation</button>
                  </div>
                </div>
              )}

              {activeTab === "doc" && (
                <div className="space-y-4">
                  <h3 className="text-[#2174C3] font-bold text-lg mb-4">Documentation</h3>
                  <div className="custom-scrollbar overflow-auto border border-gray-100 rounded-lg">
                    <table className="w-full text-sm min-w-[1000px]">
                      <thead className="bg-gray-50 text-gray-500 text-[10px] uppercase font-bold text-center border-b border-gray-100">
                        <tr>
                          <th className="p-3 w-[50px]"></th>
                          <th className="p-3">Document Type</th>
                          <th className="p-3">File Name</th>
                          <th className="p-3 w-[80px]">Drive</th>
                          <th className="p-3">File Link (URL)</th>
                          <th className="p-3">Uploader</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-100">
                        {documentationRows.map((row, idx) => (
                          <tr key={idx}>
                            <td className="p-2">
                              <button type="button" onClick={() => setDocumentationRows(prev => prev.filter((_, i) => i !== idx))} className="w-6 h-6 rounded-full bg-red-50 text-red-500 text-xs font-bold">×</button>
                            </td>
                            <td className="p-2">
                              <select
                                value={row.type}
                                onChange={(e) => { const a = [...documentationRows]; a[idx].type = e.target.value; setDocumentationRows(a); }}
                                className="w-full bg-gray-100 rounded-lg p-3 border-none focus:ring-2 focus:ring-[#2174C3] text-sm text-black"
                              >
                                <option value="">Select Type</option>
                                <option value="Invoice">Invoice</option>
                                <option value="Form IHT">Form IHT</option>
                                <option value="All Document">All Document</option>
                              </select>
                            </td>
                            <td className="p-2">
                              <input
                                type="text"
                                value={row.file_name}
                                onChange={(e) => { const a = [...documentationRows]; a[idx].file_name = e.target.value; setDocumentationRows(a); }}
                                className="w-full bg-gray-100 rounded-lg p-3 border-none focus:ring-2 focus:ring-[#2174C3] text-sm text-black"
                                placeholder="Enter file name"
                              />
                            </td>
                            <td className="p-2 text-center">
                              <button
                                type="button"
                                onClick={() => window.open('https://drive.google.com/drive/folders/1oM-ijNHhANgh7EFZvzUG_smQJBq4G77d?usp=sharing', '_blank')}
                                className="p-2 rounded-lg transition-all bg-[#2174C3] text-white hover:bg-[#1A5E9D]"
                                title="Open in Google Drive"
                              >
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                                </svg>
                              </button>
                            </td>
                            <td className="p-2">
                              <input
                                type="text"
                                value={row.url}
                                onChange={(e) => { const a = [...documentationRows]; a[idx].url = e.target.value; setDocumentationRows(a); }}
                                className="w-full bg-gray-100 rounded-lg p-3 border-none focus:ring-2 focus:ring-[#2174C3] text-sm text-black"
                                placeholder="Enter url"
                              />
                            </td>
                            <td className="p-2">
                              <select
                                value={row.submitted_by}
                                onChange={(e) => { const a = [...documentationRows]; a[idx].submitted_by = e.target.value; setDocumentationRows(a); }}
                                className="w-full bg-gray-100 rounded-lg p-3 border-none focus:ring-2 focus:ring-[#2174C3] text-sm text-black"
                              >
                                <option value="" style={{ color: '#000' }}>Select PIC</option>
                                {employees.filter(emp =>
                                  emp.role === 'Administrator' ||
                                  emp.role === 'Super Administrator' ||
                                  [200335, 200331, 200329].includes(parseInt(emp.nik)) ||
                                  parseInt(emp.nik) === parseInt(user?.nik)
                                ).map(emp => (
                                  <option key={emp.nik} value={emp.nik} style={{ color: '#000' }}>{emp.full_name}</option>
                                ))}
                              </select>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                  <button type="button" onClick={() => setDocumentationRows([...documentationRows, { type: "", file_name: "", url: "", submitted_by: "" }])} className="text-[#2174C3] font-bold text-sm">+ Add Documentation</button>
                </div>
              )}
            </div>

            <div className="flex justify-end space-x-2 mt-12">
              {isEditMode && user?.role !== 'Dean' && (
                <button type="button" onClick={handleDeleteClick} className="bg-red-500 hover:bg-red-600 text-white px-4 py-1 text-sm rounded font-medium transition-colors cursor-pointer">Delete</button>
              )}
              <button type="button" onClick={() => setShowEventModal(false)} className="bg-[#878D94] hover:bg-[#607D8B] text-white px-4 py-1 text-sm rounded font-medium transition-colors cursor-pointer">Cancel</button>
              {user?.role !== 'Dean' && (
                <button type="button" onClick={handleSaveAll} className="bg-[#2174C3] hover:bg-[#1A5E9D] text-white px-6 py-1 text-sm rounded font-medium transition-colors shadow cursor-pointer">Save</button>
              )}
            </div>
          </div>
        </div>
      )}
      {/* ─── Toast Notifications ─────────────────────────────────── */}
      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast(null)}
        />
      )}

      {/* ─── Delete Confirmation ─────────────────────────────────── */}
      <ConfirmModal
        isOpen={showDeleteConfirm}
        onClose={() => setShowDeleteConfirm(false)}
        onConfirm={handleConfirmDelete}
        title="Confirm Delete"
        message="Are you sure want to delete this Training?"
      />

      {/* Budget Modal */}
      {showBudgetModal && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
          <div className="bg-white rounded-xl shadow-2xl w-full max-w-2xl p-10 relative animate-in fade-in zoom-in duration-200 overflow-y-auto custom-scrollbar max-h-[90vh]">
            <h2 className="text-4xl font-bold text-black mb-2">Set Training Budget</h2>
            <hr className="mb-8 border-gray-200" />

            <div className="space-y-6">
              <div className="grid grid-cols-1 sm:grid-cols-3 items-center gap-2">
                <label className="text-black font-semibold">Budget Name</label>
                <input
                  type="text"
                  value={budgetName}
                  onChange={(e) => setBudgetName(e.target.value)}
                  className="sm:col-span-2 p-3 rounded-lg bg-gray-100 border-none focus:ring-2 focus:ring-[#2174C3] text-black"
                  placeholder="e.g. Annual Training Budget 2026"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 items-center gap-2">
                <label className="text-black font-semibold">Start Date</label>
                <input
                  type="date"
                  value={budgetStartDate}
                  onChange={(e) => setBudgetStartDate(e.target.value)}
                  className="sm:col-span-2 p-3 rounded-lg bg-gray-100 border-none focus:ring-2 focus:ring-[#2174C3] text-black"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 items-center gap-2">
                <label className="text-black font-semibold">End Date</label>
                <input
                  type="date"
                  value={budgetEndDate}
                  onChange={(e) => setBudgetEndDate(e.target.value)}
                  className="sm:col-span-2 p-3 rounded-lg bg-gray-100 border-none focus:ring-2 focus:ring-[#2174C3] text-black"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 items-center gap-2">
                <label className="text-black font-semibold">Total Budget</label>
                <div className="sm:col-span-2 relative">
                  <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 font-bold">IDR</span>
                  <input
                    type="number"
                    value={totalBudget}
                    onChange={(e) => setTotalBudget(e.target.value)}
                    className="w-full pl-12 pr-4 py-3 rounded-lg bg-gray-100 border-none focus:ring-2 focus:ring-[#2174C3] text-black"
                    placeholder="0"
                  />
                </div>
              </div>
            </div>

            <div className="flex justify-end space-x-2 mt-10">
              <button
                type="button"
                onClick={() => setShowBudgetModal(false)}
                className="bg-[#878D94] hover:bg-[#607D8B] text-white px-3 py-1 text-sm rounded font-medium transition-colors cursor-pointer"
              >
                Cancel
              </button>
              {user?.role !== 'Dean' && (
                <button
                  type="button"
                  onClick={handleSaveBudget}
                  className="bg-[#2174C3] hover:bg-[#1A5E9D] text-white px-4 py-1 text-sm rounded font-medium transition-colors shadow cursor-pointer"
                >
                  Save
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </MainLayout>
  );
}
