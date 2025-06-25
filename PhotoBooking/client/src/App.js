import React, { useState, useEffect } from "react";
import axios from "axios";
import studioBackground from "./img/studio.jpeg";
import "./styles.css";

function App() {
    const [clients, setClients] = useState([]);
    const [photographers, setPhotographers] = useState([]);
    const [timeslots, setTimeslots] = useState([]);
    const [availability, setAvailability] = useState({ date: "", photographerId: "", startTime: "", endTime: "" });
    const [sessionData, setSessionData] = useState({
        clientId: "",
        photographerId: "",
        timeslotId: "",
        location: "",
    });
    const [sessions, setSessions] = useState([]);
    const [availablePhotographers, setAvailablePhotographers] = useState([]);
    const [selectedDate, setSelectedDate] = useState("");

    useEffect(() => {
        fetchClients();
        fetchPhotographers();
    }, []);

    const fetchClients = async () => {
        try {
            const response = await axios.get("http://127.0.0.1:5000/clients");
            setClients(response.data.clients || []);
        } catch (error) {
            console.error("Error fetching clients:", error);
        }
    };

    const fetchPhotographers = async () => {
        try {
            const response = await axios.get("http://127.0.0.1:5000/photographers");
            setPhotographers(response.data.photographers || []);
        } catch (error) {
            console.error("Error fetching photographers:", error);
        }
    };

    const fetchAvailableTimeslots = async (photographerId) => {
        try {
            const response = await axios.get(`http://127.0.0.1:5000/photographers/${photographerId}/available-timeslots`);
            setTimeslots(response.data.available_timeslots || []);
        } catch (error) {
            console.error("Error fetching available timeslots:", error);
        }
    };

    const fetchAvailablePhotographers = async (date) => {
        try {
            const response = await axios.get(`http://127.0.0.1:5000/photographers/availability?date=${date}`);
            setAvailablePhotographers(response.data.available_photographers || []);
        } catch (error) {
            console.error("Error fetching available photographers:", error);
        }
    };

    const createAvailability = async () => {
        try {
            const transactionId = Date.now();
            const formattedData = {
                TransactionID: transactionId,
                PhotographerID: availability.photographerId,
                AvailableDate: availability.date,
                StartTime: availability.startTime,
                EndTime: availability.endTime,
            };

            if (!formattedData.PhotographerID) {
                alert("Please select a photographer.");
                return;
            }

            const response = await axios.post("http://127.0.0.1:5000/availability", formattedData);
            alert(response.data.message);
            fetchAvailableTimeslots(availability.photographerId);
        } catch (error) {
            alert(error.response?.data?.error || "Error creating availability");
        }
    };

    const scheduleSession = async () => {
        try {
            const transactionId = Date.now();
            const formattedData = {
                TransactionID: transactionId,
                ClientID: sessionData.clientId,
                PhotographerID: sessionData.photographerId,
                TimeslotID: sessionData.timeslotId,
                Location: sessionData.location,
            };
            const response = await axios.post("http://127.0.0.1:5000/bookings", formattedData);
            alert(response.data.message);
        } catch (error) {
            alert(error.response?.data?.error || "Error scheduling session");
        }
    };

    const fetchSessionsForClient = async (clientId) => {
        try {
            const response = await axios.get(`http://127.0.0.1:5000/clients/${clientId}/bookings`);
            const bookings = response.data.bookings || [];

            const enrichedSessions = await Promise.all(
                bookings.map(async (session) => {
                    try {
                        const timeslotResponse = await axios.get(
                            `http://127.0.0.1:5000/timeslots/${session.TimeslotID}`
                        );
                        const timeslot = timeslotResponse.data;

                        const photographerId = timeslot.PhotographerID || session.PhotographerID;

                        const photographer = photographers.find(
                            (p) => p.PhotographerID === photographerId
                        );

                        return {
                            ...session,
                            PhotographerID: photographerId,
                            PhotographerName: photographer ? photographer.Name : "Unknown",
                            Date: timeslot.AvailableDate,
                            StartTime: timeslot.StartTime,
                            EndTime: timeslot.EndTime,
                        };
                    } catch (error) {
                        console.error("Error fetching session details:", error);
                        return session;
                    }
                })
            );

            setSessions(enrichedSessions);
        } catch (error) {
            alert(error.response?.data?.error || "Error fetching sessions for client");
        }
    };

    const cancelSession = async (bookingId) => {
        if (!bookingId) {
            alert("Booking ID is missing!");
            return;
        }

        try {
            const transactionId = Date.now();
            const response = await axios.delete(`http://127.0.0.1:5000/bookings/${bookingId}`, {
                params: { TransactionID: transactionId },
            });

            alert(response.data.message);

            setSessions((prevSessions) => prevSessions.filter((session) => session.BookingID !== bookingId));

        } catch (error) {
            console.error("Error canceling session:", error);
            alert(error.response?.data?.error || "Error canceling session");
        }
    };


    const updateSessionLocation = async (bookingId) => {
        if (!bookingId) {
            alert("Booking ID is missing!");
            return;
        }

        const newLocation = prompt("Enter the new location:");
        if (!newLocation) return;

        try {
            const transactionId = Date.now();
            const response = await axios.put(`http://127.0.0.1:5000/bookings/${bookingId}`, {
                TransactionID: transactionId,
                Location: newLocation,
            });

            alert(response.data.message);

            setSessions((prevSessions) =>
                prevSessions.map((session) =>
                    session.BookingID === bookingId ? { ...session, Location: newLocation } : session
                )
            );
        } catch (error) {
            console.error("Error updating session location:", error);
            alert(error.response?.data?.error || "Error updating session location");
        }
    };



    return (
        <div className="app-container">
            <header className="header">
                <h1>Photo Booking Management</h1>
            </header>
            <img src={studioBackground} alt="Studio Background" className="studio-image" />
            <main className="main-content">
                {/* Create Photographer Availability */}
                <section className="card">
                    <h2>Create Photographer Availability</h2>
                    <input
                        type="date"
                        value={availability.date}
                        onChange={(e) => setAvailability({ ...availability, date: e.target.value })}
                    />
                    <select
                        onChange={(e) => setAvailability({ ...availability, photographerId: e.target.value })}
                    >
                        <option>Select Photographer</option>
                        {photographers.map((photographer) => (
                            <option key={photographer.PhotographerID} value={photographer.PhotographerID}>
                                {photographer.Name}
                            </option>
                        ))}
                    </select>
                    <input
                        type="time"
                        value={availability.startTime}
                        onChange={(e) => setAvailability({ ...availability, startTime: e.target.value })}
                    />
                    <input
                        type="time"
                        value={availability.endTime}
                        onChange={(e) => setAvailability({ ...availability, endTime: e.target.value })}
                    />
                    <button onClick={createAvailability}>Create Availability</button>
                </section>

                {/* Schedule a Session */}
                <section className="card">
                    <h2>Schedule a Session</h2>
                    <select onChange={(e) => setSessionData({ ...sessionData, clientId: e.target.value })}>
                        <option>Select Client</option>
                        {clients.map((client) => (
                            <option key={client.ClientID} value={client.ClientID}>
                                {client.Name}
                            </option>
                        ))}
                    </select>
                    <select
                        onChange={(e) => {
                            setSessionData({ ...sessionData, photographerId: e.target.value });
                            fetchAvailableTimeslots(e.target.value);
                        }}
                    >
                        <option>Select Photographer</option>
                        {photographers.map((photographer) => (
                            <option key={photographer.PhotographerID} value={photographer.PhotographerID}>
                                {photographer.Name}
                            </option>
                        ))}
                    </select>
                    <select onChange={(e) => setSessionData({ ...sessionData, timeslotId: e.target.value })}>
                        <option>Select Timeslot</option>
                        {timeslots.map((timeslot) => (
                            <option key={timeslot.TimeslotID} value={timeslot.TimeslotID}>
                                {timeslot.AvailableDate} {timeslot.StartTime}-{timeslot.EndTime}
                            </option>
                        ))}
                    </select>
                    <input
                        type="text"
                        value={sessionData.location}
                        onChange={(e) => setSessionData({ ...sessionData, location: e.target.value })}
                        placeholder="Location"
                    />
                    <button onClick={scheduleSession}>Schedule Session</button>
                </section>

                <section className="card">
                    <h2>View Scheduled Photoshoots of a Client</h2>
                    <select onChange={(e) => fetchSessionsForClient(e.target.value)}>
                        <option>Select Client</option>
                        {clients.map((client) => (
                            <option key={client.ClientID} value={client.ClientID}>
                                {client.Name}
                            </option>
                        ))}
                    </select>

                    <div className="session-container">
                        {sessions.map((session) => (
                            <div key={session.BookingID} className="session-card">
                                <h3>{session.PhotographerName || "Unknown Photographer"}</h3>
                                <p>
                                    📅 <strong>{session.Date || "Unknown Date"}</strong> <br />
                                    🕒 {session.StartTime || "Unknown Start"} - {session.EndTime || "Unknown End"} <br />
                                    📍 {session.Location || "Unknown Location"}
                                </p>
                                <div className="session-actions">
                                    <button className="cancel-btn" onClick={() => cancelSession(session.BookingID)}>
                                        ❌ Cancel
                                    </button>
                                    <button
                                        className="update-btn"
                                        onClick={() => updateSessionLocation(session.BookingID)}
                                    >
                                        ✏️ Update Location
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>

                </section>

                {/* Find Available Photographers */}
                <section className="card">
                    <h2>Find Available Photographers</h2>
                    <input
                        type="date"
                        value={selectedDate}
                        onChange={(e) => {
                            setSelectedDate(e.target.value);
                            fetchAvailablePhotographers(e.target.value);
                        }}
                    />
                    <ul>
                        {availablePhotographers.length > 0 ? (
                            availablePhotographers.map((photographer) => (
                                <li key={photographer.PhotographerID}>
                                    {photographer.Name} - Specialty: {photographer.Specialty}
                                </li>
                            ))
                        ) : (
                            <li>No photographers available for the selected date.</li>
                        )}
                    </ul>
                </section>
            </main>
        </div>
    );
}

export default App;
