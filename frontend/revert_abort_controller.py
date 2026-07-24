import re

def fix_file(filepath, fetch_func_name):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # We need to replace the AbortController logic with ignore pattern in useCallback
    
    if fetch_func_name == 'fetchTrainings':
        # Replace the useCallback definition
        content = re.sub(
            r"const fetchTrainings = useCallback\(async \(signal\) => \{.*?\n  \}, \[page, search, division, month, selectedYear, activeView\]\);",
            r"""const fetchTrainings = useCallback(async (ignoreFlag = { current: false }) => {
    setLoading(true);
    try {
      const res = await api.get(
        `/api/training-master/?page=${page}&search=${search}&division=${division}&month=${month}&year=${selectedYear}&view_mode=${activeView}`
      );
      if (!ignoreFlag.current && res && res.data) {
        const results = res.data.results || res.data;
        const count = res.data.count || (Array.isArray(res.data) ? res.data.length : results.length);
        setTrainings(results || []);
        setTotalCount(count);
        setTotalPages(Math.ceil(count / 50) || 1);
      }
    } catch (e) {
      if (!ignoreFlag.current) console.warn("API Error during fetchTrainings", e);
    } finally {
      if (!ignoreFlag.current) setLoading(false);
    }
  }, [page, search, division, month, selectedYear, activeView]);""",
            content,
            flags=re.DOTALL
        )
        
        # Replace the useEffect
        content = re.sub(
            r"useEffect\(\(\) => \{\s*const controller = new AbortController\(\);\s*fetchTrainings\(controller\.signal\);\s*return \(\) => controller\.abort\(\);\s*\}, \[fetchTrainings\]\);",
            r"""useEffect(() => {
    const ignoreFlag = { current: false };
    fetchTrainings(ignoreFlag);
    return () => { ignoreFlag.current = true; };
  }, [fetchTrainings]);""",
            content,
            flags=re.DOTALL
        )
        
    elif fetch_func_name == 'fetchParticipants':
        # Replace the useCallback definition
        content = re.sub(
            r"const fetchParticipants = useCallback\(async \(signal\) => \{.*?\n    \}, \[searchTerm, divisionFilter, courseFilter, activeYear, activeView, isMyTna\]\);",
            r"""const fetchParticipants = useCallback(async (ignoreFlag = { current: false }) => {
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
            if (!ignoreFlag.current) {
                setParticipants(res.data);
            }
        } catch (err) {
            if (!ignoreFlag.current) console.error('Failed to fetch participants:', err);
        } finally {
            if (!ignoreFlag.current) setLoading(false);
        }
    }, [searchTerm, divisionFilter, courseFilter, activeYear, activeView, isMyTna]);""",
            content,
            flags=re.DOTALL
        )
        
        # Replace the useEffect
        content = re.sub(
            r"useEffect\(\(\) => \{\s*const controller = new AbortController\(\);\s*fetchParticipants\(controller\.signal\);\s*return \(\) => controller\.abort\(\);\s*\}, \[fetchParticipants\]\);",
            r"""useEffect(() => {
        const ignoreFlag = { current: false };
        fetchParticipants(ignoreFlag);
        return () => { ignoreFlag.current = true; };
    }, [fetchParticipants]);""",
            content,
            flags=re.DOTALL
        )

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

fix_file("c:/xampp/htdocs/capstone-project/frontend/src/pages/TrainingMasterPage.jsx", "fetchTrainings")
fix_file("c:/xampp/htdocs/capstone-project/frontend/src/pages/TnaPage.jsx", "fetchParticipants")
print("Done fixing ignore flags")
