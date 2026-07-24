import re

def add_ignore_pattern_to_file(filepath, fetch_func_name):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # We want to find the useEffect that calls fetch_func_name()
    # It usually looks like:
    # useEffect(() => {
    #     fetchData();
    # }, [fetchData]);
    
    pattern = rf"useEffect\(\(\) => {{\s*({fetch_func_name}\([^)]*\);)\s*}}, \[([^\]]*)\]\);"
    
    # Since fetch_func_name itself might be the one we need to modify... Wait.
    # If the fetch function is defined with useCallback, it's easier to modify the useCallback to take a signal,
    # or just modify the useEffect to NOT use useCallback and put the fetch logic inside useEffect.
    # Alternatively, the easiest way to fix React race condition without refactoring useCallback is:
    
    # Let's write custom replacements for each file.
    pass

# For EmployeePage.jsx
with open("c:/xampp/htdocs/capstone-project/frontend/src/pages/EmployeePage.jsx", "r", encoding="utf-8") as f:
    emp_content = f.read()
    
emp_replacement = """    useEffect(() => {
        let ignore = false;
        
        const loadData = async () => {
            setLoading(true);
            try {
                const [empRes, divRes] = await Promise.all([
                    api.get(`/api/employee/?page=${currentPage}&search=${searchTerm}&division=${isMyData ? '' : (selectedDivision === 'All Division' ? '' : selectedDivision)}&year=${selectedYear}&view_mode=${activeView}`),
                    api.get('/api/divisions/')
                ]);

                if (!ignore) {
                    if (empRes.data.results) {
                        setEmployees(empRes.data.results);
                        setTotalCount(empRes.data.count);
                        setTotalPages(Math.ceil(empRes.data.count / ITEMS_PER_PAGE));
                    } else {
                        setEmployees(empRes.data);
                        setTotalCount(empRes.data.length);
                        setTotalPages(Math.ceil(empRes.data.length / ITEMS_PER_PAGE));
                    }
                    setDivisions(divRes.data);
                }
            } catch (err) {
                if (!ignore) console.error('Failed to fetch data:', err);
            } finally {
                if (!ignore) setLoading(false);
            }
        };

        loadData();

        return () => {
            ignore = true;
        };
    }, [currentPage, searchTerm, selectedDivision, selectedYear, activeView, isMyData]);"""

# Replace the old useCallback and useEffect with the new useEffect
emp_old_pattern = re.compile(r"const fetchData = useCallback\(async \(\) => \{.*?\}, \[.*?\]\);\s*useEffect\(\(\) => \{\s*fetchData\(\);\s*\}, \[fetchData\]\);", re.DOTALL)
emp_content = emp_old_pattern.sub(emp_replacement, emp_content)

with open("c:/xampp/htdocs/capstone-project/frontend/src/pages/EmployeePage.jsx", "w", encoding="utf-8") as f:
    f.write(emp_content)

# For TnaPage.jsx
with open("c:/xampp/htdocs/capstone-project/frontend/src/pages/TnaPage.jsx", "r", encoding="utf-8") as f:
    tna_content = f.read()

tna_replacement = """    useEffect(() => {
        let ignore = false;
        const loadParticipants = async () => {
            setLoading(true);
            try {
                const params = {
                    search: searchTerm,
                };
                if (!isMyTna && divisionFilter && divisionFilter !== 'All Division') params.division = divisionFilter;
                if (!isMyTna && courseFilter && courseFilter !== 'All Course') params.course_name = courseFilter;
                if (activeYear) params.year = activeYear;
                params.view_mode = activeView;

                const res = await api.get('/api/tna-participant/', { params });
                if (!ignore) {
                    setParticipants(res.data);
                }
            } catch (err) {
                if (!ignore) console.error('Failed to fetch participants:', err);
            } finally {
                if (!ignore) setLoading(false);
            }
        };

        loadParticipants();

        return () => {
            ignore = true;
        };
    }, [searchTerm, divisionFilter, courseFilter, activeYear, activeView, isMyTna]);"""

tna_old_pattern = re.compile(r"const fetchParticipants = useCallback\(async \(\) => \{.*?\}, \[.*?\]\);\s*useEffect\(\(\) => \{\s*fetchParticipants\(\);\s*\}, \[fetchParticipants\]\);", re.DOTALL)
tna_content = tna_old_pattern.sub(tna_replacement, tna_content)

with open("c:/xampp/htdocs/capstone-project/frontend/src/pages/TnaPage.jsx", "w", encoding="utf-8") as f:
    f.write(tna_content)

# For TrainingMasterPage.jsx
with open("c:/xampp/htdocs/capstone-project/frontend/src/pages/TrainingMasterPage.jsx", "r", encoding="utf-8") as f:
    tm_content = f.read()

tm_replacement = """  useEffect(() => {
    let ignore = false;
    const loadTrainings = async () => {
      setLoading(true);
      try {
        const res = await api.get(
          `/api/training-master/?page=${page}&search=${search}&division=${division}&month=${month}&year=${selectedYear}&view_mode=${activeView}`
        );
        if (!ignore && res && res.data) {
          const results = res.data.results || res.data;
          const count = res.data.count || (Array.isArray(res.data) ? res.data.length : results.length);
          setTrainings(results || []);
          setTotalCount(count);
          setTotalPages(Math.ceil(count / 50) || 1);
        }
      } catch (e) {
        if (!ignore) console.warn("API Error during fetchTrainings", e);
      } finally {
        if (!ignore) setLoading(false);
      }
    };

    loadTrainings();

    return () => {
      ignore = true;
    };
  }, [page, search, division, month, selectedYear, activeView]);"""

tm_old_pattern = re.compile(r"const fetchTrainings = useCallback\(async \(\) => \{.*?\}, \[.*?\]\);\s*useEffect\(\(\) => \{\s*fetchTrainings\(\);\s*\}, \[fetchTrainings\]\);", re.DOTALL)
tm_content = tm_old_pattern.sub(tm_replacement, tm_content)

# Also fix the pagination condition in TrainingMasterPage.jsx
# Replace `{totalPages > 1 ? (` with just `True` or directly remove the condition
tm_content = re.sub(r"\{totalPages > 1 \? \((.*?)\) : \((.*?)\)\}", r"\1", tm_content, flags=re.DOTALL)

with open("c:/xampp/htdocs/capstone-project/frontend/src/pages/TrainingMasterPage.jsx", "w", encoding="utf-8") as f:
    f.write(tm_content)

print("Done")
