function setupAvatarSpinner() {
    const spinner = document.getElementById("avatar-spinner");
    const images = document.querySelectorAll(".container_avatares img");
    if (!spinner || !images.length) return;

    let loaded = 0;
    const total = images.length;

    function hideSpinner() {
        spinner.style.display = "none";
    }

    images.forEach((img) => {
        if (img.complete) {
            loaded++;
            if (loaded === total) hideSpinner();
        } else {
            img.addEventListener("load", () => {
                loaded++;
                if (loaded === total) hideSpinner();
            });
            img.addEventListener("error", () => {
                loaded++;
                if (loaded === total) hideSpinner();
            });
        }
    });

    // Fallback por si algún evento no se dispara
    setTimeout(hideSpinner, 3000);
}

function setupAvatarSelection() {
    const container = document.querySelector(".container_avatares");
    if (!container) return;

    const updateUrl = container.getAttribute("data-update-url");
    const avatarPrefix =
        container.getAttribute("data-avatar-prefix") || "/static/images/avatares/";
    const buttons = container.querySelectorAll(".avatar-btn");
    if (!updateUrl || !buttons.length) return;

    buttons.forEach((btn) => {
        btn.addEventListener("click", async () => {
            const avatar = btn.getAttribute("data-avatar");
            if (!avatar) return;

            // Marcar seleccionado en UI inmediatamente
            buttons.forEach((b) => {
                const avatarDiv = b.querySelector(".avatar");
                if (avatarDiv) {
                    avatarDiv.classList.remove("avatar-selected");
                }
            });
            const currentAvatarDiv = btn.querySelector(".avatar");
            if (currentAvatarDiv) {
                currentAvatarDiv.classList.add("avatar-selected");
            }

            try {
                await fetch(updateUrl, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-Requested-With": "XMLHttpRequest",
                    },
                    body: JSON.stringify({ avatar }),
                });

                // Actualizar avatar en el header sin recargar
                const headerAvatar = document.getElementById("headerAvatar");
                if (headerAvatar) {
                    headerAvatar.src = avatarPrefix + avatar;
                }

                // Actualizar avatar grande dentro de la vista de perfil
                const profileAvatar = document.getElementById("profileAvatar");
                if (profileAvatar) {
                    profileAvatar.src = avatarPrefix + avatar;
                }
            } catch (e) {
                // Si falla, no recargamos la página; el usuario puede intentar de nuevo
                // Opcionalmente aquí se podría mostrar un mensaje en consola
                console.error("Error actualizando avatar", e);
            }
        });
    });
}

document.addEventListener("DOMContentLoaded", function () {
    setupAvatarSpinner();
    setupAvatarSelection();
});

