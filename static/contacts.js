const serverSession = "session=" + getSession("client_session").value;

// Load the entire list
(async function() {
    //await sleep(3000);
    const emergencyContacts = await getEmergencyContacts();
    
    if (emergencyContacts.length == 0) {
        // TODO: Add a nice "No contacts" alert
    }

    for (let i = 0; i < emergencyContacts.length; i++) {
        
        const ice = emergencyContacts[i];

        const onRemoveButtonClicked = async event => {
            const response = await deleteEmergencyContact(ice.id);

            if (response.status != 200) {
                console.log("Something went wrong during the request");
                return;
            }

            document.getElementById("eid-" + ice.id).remove();
        };

        // Create list item and add to DOM
        addToList("eid-" + ice.id, ice.phone_number, onRemoveButtonClicked);
    }
})();

const addToList = (function () {
    // Constructs the addToList function.
    // Clones the placeholder list item from DOM and then deletes it.

    const contactList = document.getElementById("contact-list");

    const li = document.getElementById("listItemBlueprint");
    const pn = li.getElementsByClassName("phone-number")[0];

    pn.innerHTML = "";

    contactList.removeChild(li);

    // The addToList function
    return (idAttribute, phoneNumber, onRemove) => {
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

        const phoneNumberText = listItem.getElementsByClassName("phone-number")[0];
        phoneNumberText.innerHTML = phoneNumber;

        contactList.appendChild(listItem);
    };
})();

async function getEmergencyContacts() {
    return fetch('http://127.0.0.1:5000/api/device/ec', {
        method: "GET",
        headers: {
            Cookie: serverSession
        }
    }).then(r => r.json());
}

async function addEmergencyContact(ec) {
    console.log(JSON.stringify(ec));
    return fetch("http://127.0.0.1:5000/api/device/ec", {
        method: "POST",
        headers: {
            Cookie: serverSession,
            "Content-Type": "application/json"
        },
        body: JSON.stringify(ec)
    });
}

async function deleteEmergencyContact(id) {
    return response = fetch("http://127.0.0.1:5000/api/device/ec/" + id, {
        method: "DELETE",
        headers: {
            Cookie: serverSession
        }
    });
}

async function onSaveButtonClicked() {
    const saveButton = document.getElementById("saveButton");
    const saveText = document.getElementById("saveText");
    const spinner = document.getElementById("saveSpinner");

    const phoneNumberInput = document.getElementById("phoneNumberInput");
    const phoneNumber = phoneNumberInput.value;
    
    saveButton.disabled = true;
    saveText.innerHTML = "Saving";
    spinner.hidden = false;

    let response = null;

    try {
        await sleep(500);

        response = await addEmergencyContact({
            phone_number: phoneNumber
        });
    }
    catch (e) {
        // TODO: Error message
        return;
    }
    finally {
        saveText.innerHTML = "Save";
        spinner.hidden = true;
        saveButton.disabled = false;
    }

    if (response.status != 200) {
        // TODO: Error message
        return;
    }

    const ecId = await response.text();

    addToList("eid-" + ecId, phoneNumber, async _ => {
        const r = await deleteEmergencyContact(ecId);

        if (r.status != 200) {
            // TODO: Error message
            return;
        }

        const listItem = document.getElementById("eid-" + ecId);
        listItem.remove();
    });
}

async function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}