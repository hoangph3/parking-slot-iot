document.addEventListener("DOMContentLoaded", function() {
  const numRows = 5;
  const numCols = 10;
  var currentSlot = 0;

  const parkingMap = document.querySelector(".parking-map");

  for (let row = 1; row <= numRows; row++) {
    const parkingRow = document.createElement("div");
    parkingRow.classList.add("parking-row");
    for (let col = 1; col <= numCols; col++) {
      currentSlot += 1;
      const parkingSlot = document.createElement("div");
      parkingSlot.classList.add("parking-slot");
      // parkingSlot.textContent = row + "-" + col;
      let slot = currentSlot
      parkingSlot.setAttribute("id", "slot" + "-" + slot)
      parkingSlot.textContent = slot;
      // Randomly assign slot availability
      parkingSlot.classList.add("available");
      parkingRow.appendChild(parkingSlot);
    }
    parkingMap.appendChild(parkingRow);
  }

  function updateParkingStatus() {
    // Make a fetch request to your server-side API to get the latest slot status
    fetch("/api/status")
      .then((response) => response.json())
      .then((data) => {
        updateSlots(data);
        console.log(data);
      })
      .catch((error) => {
        console.error("Error fetching data: ", error);
      });
  }

  function updateSlots(data) {
    // Update the status of existing slots based on the data received
    for (let i = 0; i < data.length; i++) {
      slotIndex = i + 1;
      // console.log(i, data[i]);
      const parkingSlot = document.getElementById("slot" + "-" + slotIndex);
      // console.log(parkingSlot);
      parkingSlot.classList.remove("unavailable", "available");
      parkingSlot.classList.add(data[i] ? "unavailable" : "available");
    }
    // Count available slots
    const availableSlot = document.getElementsByClassName("available").length;
    document.getElementById("count").textContent = availableSlot;
  }

  // Update the parking status every 5 seconds (adjust interval as needed)
  setInterval(updateParkingStatus, 5000);

  // Initial update to display the slots when the page loads
  updateParkingStatus();

});
