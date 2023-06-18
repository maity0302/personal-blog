let toggleItems = document.querySelectorAll(".menu--items li");
let mainContent = document.getElementById("main--content");
let customersProduct = document.getElementById("customersProduct");
let customersManager = document.getElementById("customersManager");

let removeActive = () => {
    toggleItems.forEach(item => {
        item.classList.remove("active");
    })
}

toggleItems.forEach(item => {
    item.addEventListener("click", (e) => {
        removeActive();
        e.target.classList.add("active");
        if (e.target.id === "toproducts") {
            mainContent.innerHTML = products;
        } else if (e.target.id === "tocustomers") {
            mainContent.innerHTML = customers;
        } else {
            window.location.reload();
        }
    })
});


customersProduct.addEventListener("click", () => {
    mainContent.innerHTML = products;
    removeActive();
    document.getElementById("toproducts").classList.add("active");
})
customersManager.addEventListener("click", () => {
    mainContent.innerHTML = customers;
    removeActive();
    document.getElementById("tocustomers").classList.add("active");
})