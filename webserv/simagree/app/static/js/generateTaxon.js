$(document).ready(() => {
    data = $('#prevTaxSelect option');
    $('.chosen-select').chosen({
        width: '50%'
    });

    // renvoie l'indice du taxon suivant (prend l'indice du taxon en paramètre)
    function getNextTaxon(tax_ind) {
        for (let i = tax_ind; i < data.length - 1; i++) {
            if (parseInt(data[i].value, 10) < parseInt(data[i+1].value, 10)) {
                return i+1;
            }
        }
        return tax_ind;
    }

    // renvoie le nouveau taxon
    // prend en paramètres la valeur du taxon sélectionné et l'indice du taxon suivant
    function getNewTaxon(current, next) {
        if (current == next) {
            return current + 100;
        }
        let add_list = [100, 50, 25, 10, 5, 1];
        for (let k = 0; k < add_list.length; k++) {
            if (current + add_list[k] < next) {
                return current + add_list[k];
            }
        }
        return current + 1;
    }

    $('#taxBtn').on('click', (e) => {
        e.preventDefault();
        let choice = $('#prevTaxSelect').prop('selectedIndex');
        let next = getNextTaxon(choice);
        console.log(choice);
        let suiv = getNewTaxon(parseInt(data[choice].value, 10), parseInt(data[next].value, 10));
        console.log(suiv);
        $("#id_taxon").val(suiv);
        $('#taxonModal').modal('hide');
    });
    
    $('#taxLinkBtn').on('click', (e) => {
        e.preventDefault();
        $('#id_tax').val(parseInt($('#prevTaxSelect').val(),10));
        $('#taxonModal').modal('hide');
    })

    $('#maxTaxBtn').on('click', (e) => {
        e.preventDefault();
        $('#id_taxon').val(parseInt($('#maxTaxIn').val(), 10));
        $('#taxonModal').modal('hide');
    })
});
