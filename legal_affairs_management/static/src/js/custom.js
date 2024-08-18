$(document).ready(function() {
    console.log("legal custom", $('#legal_case_table').length)
    console.log("table custom", $('.table').length)
    $('#legal_case_table').DataTable({
        "paging": true,         // Enable pagination
        "searching": true,      // Enable search box
        "ordering": true,       // Enable sorting
        "info": true            // Show information (e.g., "Showing 1 to 10 of 50 entries")
    });
});
