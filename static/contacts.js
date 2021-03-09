const originBaseUrl = window.location.origin;
const serverSession = "session=" + getSession("client_session").value;

// Load the entire list
(async function() {
    //await sleep(3000);
    const emergencyContacts = await getEmergencyContacts();

    console.log(emergencyContacts);
    
    if (emergencyContacts.length == 0) {
        showStatusAlert(
            AlertType.PRIMARY, 
            "No emergency contacts are registered for your device.", 
            NaN); // <- Persist
    }

    for (let i = 0; i < emergencyContacts.length; i++) {
        
        const ice = emergencyContacts[i];

        const onRemoveButtonClicked = createOnRemoveButtonEventHandler(ice.id);

        // Create list item and add to DOM
        addToList("eid-" + ice.id, ice.name, ice.phone_number, onRemoveButtonClicked);
    }
})();

// Create an event handler unique to the list item
function createOnRemoveButtonEventHandler(ecId) {
    return async event => {
        event.preventDefault();

        let response = null;

            try {
                response = await deleteEmergencyContact(ecId);
            }
            catch (e) {
                showStatusAlert(
                    AlertType.DANGER,
                    `An unknown error ocurred: ${e}`,
                    10000
                );
                return;
            }

            if (response.status != 200) {

                if (response.status == 401) {
                    showStatusAlert(
                        AlertType.WARNING,
                        "Your session token has expired. Please refresh the page to login.",
                        10000);
                    return;
                }

                showStatusAlert(
                    AlertType.DANGER, 
                    `Something happened during the request. Server responded with ${response.status}.`, 
                    10000);

                return;
            }

            document.getElementById("eid-" + ecId).remove();
    }    
}

const addToList = (function () { // Note: this function is constructed

    // Clone the placeholder list item from DOM and then delete it.
    const contactList = document.getElementById("contact-list");

    const li = document.getElementById("listItemBlueprint");
    const pn = li.getElementsByClassName("phone-number")[0];

    pn.innerHTML = "";

    contactList.removeChild(li);

    // The addToList function
    return (idAttribute, contactName, phoneNumber, onRemove) => {
        const listItem = li.cloneNode(true);

        // Set the tag's id attribute to ice id so that we can refer back
        // to it when we want to remove from the list
        listItem.id = idAttribute;

        const removeButton = listItem.getElementsByClassName("remove")[0];

        removeButton.addEventListener("click", async event => {
            event.preventDefault();

            const button = document.getElementById(idAttribute).getElementsByTagName("button")[0];
            const iTag = button.getElementsByTagName("i")[0];
            const spinner = button.getElementsByTagName("div")[0];

            // Indicate the user that the request is loading
            button.disabled = true;
            iTag.hidden = true;
            spinner.hidden = false;

            await sleep(500);

            try {
                await onRemove(event);
            }
            catch (e) {
                throw e;
            }
            finally {
                // Indicate the user that the request has done loading
                iTag.hidden = false;
                spinner.hidden = true;
                button.disabled = false;
            }
        });

        const contactNameText = listItem.getElementsByClassName("contact-name")[0];
        const phoneNumberText = listItem.getElementsByClassName("phone-number")[0];

        console.log(contactNameText);

        const formatted = tryFormatPhoneNumber(phoneNumber);
        if (formatted) {
            phoneNumberText.innerHTML = formatted;
        }
        else {
            phoneNumberText.innerHTML = phoneNumber;
        }

        contactNameText.innerHTML = contactName;

        contactList.appendChild(listItem);
    };
})();

async function getEmergencyContacts() {
    return fetch(`${originBaseUrl}/api/device/ec`, {
        method: "GET",
        headers: {
            Cookie: serverSession
        }
    }).then(r => r.json());
}

async function addEmergencyContact(ec) {
    return fetch(`${originBaseUrl}/api/device/ec`, {
        method: "POST",
        headers: {
            Cookie: serverSession,
            "Content-Type": "application/json"
        },
        body: JSON.stringify(ec)
    });
}

async function deleteEmergencyContact(id) {
    return response = fetch(`${originBaseUrl}/api/device/ec/${id}`, {
        method: "DELETE",
        headers: {
            Cookie: serverSession
        }
    });
}

async function phoneNumberInputListener(src) {
    const pattern = /^(\+\d{2}\s?\d{2}(\-|\s)?\d{3}\s?\d{2}\s?\d{2})$/;
    
    const saveButton = document.getElementById("saveButton");

    if (src.value == "") {
        src.classList.remove("is-invalid");
        src.classList.remove("is-valid");
        return;
    }

    if (pattern.test(src.value)) {
        if (src.classList.contains("is-invalid"));
            src.classList.remove("is-invalid");
        src.classList.add("is-valid");
        saveButton.disabled = false;
    }
    else {
        if (src.classList.contains("is-valid"))
            src.classList.remove("is-valid");
        src.classList.add("is-invalid");
        saveButton.disabled = true;
    }
}

async function contactNameInputListener(src) {
    const saveButton = document.getElementById("saveButton");

    if (src.value == "") {
        src.classList.remove("is-invalid");
        src.classList.remove("is-valid");
        return;
    }

    if (src.classList.contains("is-invalid"));
            src.classList.remove("is-invalid");

    src.classList.add("is-valid");
    saveButton.disabled = false;
}

async function onSaveButtonClicked() {
    // Button components
    const saveButton = document.getElementById("saveButton");
    const saveText = document.getElementById("saveText");
    const spinner = document.getElementById("saveSpinner");

    const contactNameInput = document.getElementById("contactNameInput");
    const phoneNumberInput = document.getElementById("phoneNumberInput");

    let contactName = contactNameInput.value;

    let phoneNumber = phoneNumberInput.value;
    let phoneNumberNormalized = "";
    
    // Removes special characters (except +)
    for (let i = 0; i < phoneNumber.length; i++) {
        if (/^[\d\+]$/.test(phoneNumber[i]))
            phoneNumberNormalized += phoneNumber[i];
    }

    saveButton.disabled = true;
    saveText.innerHTML = "Saving";
    spinner.hidden = false;

    let response = null;

    try {
        await sleep(500);

        response = await addEmergencyContact({
            name: contactName,
            phone_number: phoneNumberNormalized
        });
    }
    catch (e) {
        showStatusAlert(
            AlertType.DANGER,
            `An unknown error ocurred: ${e}`,
            10000
        );
        return;
    }
    finally {
        saveText.innerHTML = "Save";
        spinner.hidden = true;

        phoneNumberInput.value = "";
        phoneNumberInput.classList.remove("is-valid");

        collapseAddContactPanel();
    }

    if (response.status != 200) {
        
        if (response.status == 401) {
            showStatusAlert(
                AlertType.WARNING,
                "Your session token has expired. Please refresh the page to login.",
                10000);
            return;
        }

        showStatusAlert(
            AlertType.DANGER, 
            `Something happened during the request. Server responded with ${response.status}.`, 
            10000);
        return;
    }

    const ecId = await response.text();

    const onRemoveButtonClicked = createOnRemoveButtonEventHandler(ecId);

    addToList("eid-" + ecId, contactName, tryFormatPhoneNumber(phoneNumberNormalized), onRemoveButtonClicked);

    showStatusAlert(AlertType.SUCCESS, "The recepient was successfully added to your contact list!", 5000);
}

async function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function showStatusAlert(clazz, message, duration) {
    const statusAlert = document.getElementById("statusAlert");
    
    // Remove existing bootrap classes
    statusAlert.classList.remove(AlertType.PRIMARY);
    statusAlert.classList.remove(AlertType.SECONDARY);
    statusAlert.classList.remove(AlertType.SUCCESS);
    statusAlert.classList.remove(AlertType.DANGER);
    statusAlert.classList.remove(AlertType.WARNING);
    statusAlert.classList.remove(AlertType.INFO);
    statusAlert.classList.remove(AlertType.LIGHT);
    statusAlert.classList.remove(AlertType.DARK);

    // Remove existing text
    statusAlert.innerHTML = "";

    // Apply new
    statusAlert.classList.add(clazz);
    statusAlert.innerHTML = message;

    // Show
    $("#statusCollapse").collapse("show");

    // Wait the specified duration before the alert disappears
    await sleep(duration);

    // Hide
    $("#statusCollapse").collapse("hide");
}

function collapseAddContactPanel() {
    $("#addContactPanel").collapse("hide")
}

const AlertType = class {
    static PRIMARY = "alert-primary";
    static SECONDARY = "alert-secondary";
    static SUCCESS = "alert-success";
    static DANGER = "alert-danger";
    static WARNING = "alert-warning";
    static INFO = "alert-info";
    static LIGHT = "alert-light";
    static DARK = "alert-dark";
};

// Helpers

// Returns null if failed to format
function tryFormatPhoneNumber(str) {
    const internationalMobilePattern = /^\+(\d{2})(\d{2})(\d{3})(\d{2})(\d{2})$/;
    const localMobilePattern = /^(\d{3})(\d{3})(\d{2})(\d{2})$/;

    const internationalLandlinePattern = /^\+(\d{2})(\d{2,3})(\d{3})(\d{2})$/;
    const localLandlinePattern = /^(\d{3,4})(\d{3})(\d{2})$/;

    if (internationalMobilePattern.test(str)) {
        const segments = internationalMobilePattern.exec(str);
        return `+${segments[1]} ${segments[2]}-${segments[3]} ${segments[4]} ${segments[5]}`;
    }
    else if (localMobilePattern.test(str)) {
        const segments = localMobilePattern.exec(str);
        return `${segments[1]}-${segments[2]} ${segments[3]} ${segments[4]}`;
    }
    else if (internationalLandlinePattern.test(str)) {
        const segments = internationalLandlinePattern.exec(str);
        return `+${segments[1]} ${segments[2]}-${segments[3]} ${segments[4]}`;
    }
    else if (localLandlinePattern.test(str)) {
        const segments = localLandlinePattern.exec(str);
        return `${segments[1]}-${segments[2]} ${segments[3]}`;
    }
    
    return null;
}