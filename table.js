// fetch("./data.json")
//     .then(response => {
//         return response.json();
//     })
//     .then(dataSet => console.log(dataSet));
function format(dataSet) {
    var response = '<aside><dl>';

    if (dataSet.instructions != undefined) {
        response += '<dt>Instrucciones:</dt><dd>';
        dataSet.instructions.forEach(instruction => {
            response += instruction + '</br>';
        });
        response += '</dd>';
    };

    if (dataSet.tips != undefined) {
        response += '<dt>Sugerencias:</dt><dd>';
        dataSet.tips.forEach(tip => {
            response += tip + '</br>';
        });
        response += '</dd>';
    };

    if (dataSet.URL != undefined) {
        response += '<dt>Enlace:</dt><dd><a target="_blank" href="' + dataSet.URL + '">Garmin</a></dd>';
    };

    if (dataSet.thumbnail != undefined) {
        response += '<dt>Imágenes:</dt><dd>';
        dataSet.thumbnail.forEach(imagen => {
            response += '<a class="image featured" href="https://connectvideo.garmin.com' + imagen.replace(".jpg", ".mp4") +
                '"><img style:"min-width:62em max-width:75em" src="https://connectvideo.garmin.com' + imagen + '" /></a>';
        });
        response += '</dd>';
    };
    response += '</dl></aside>';

    return response;
}

function runPythonScript() {
    // Get the path to the Python script.
    var pythonScriptPath = "garmin.py";
    // Run the Python script.
    subprocess.run(["python", pythonScriptPath]);
}


let table = new DataTable('#example', {
    language: {
        url: 'https://cdn.datatables.net/plug-ins/1.13.7/i18n/es-ES.json',
    },
    columns: [
        { data: 'Category', title: 'Categoria' },
        { data: 'Name', title: 'Ejercicio' },
        { data: 'primaryMuscles', title: 'Músculos principales' },
        {
            data: 'secondaryMuscles',
            title: 'Músculos secundarios',
            render: {
                _: '[, ]'
            }
        },
        {
            data: 'equipment',
            title: 'Equipo'
        },
        {
            data: 'heroImage',
            title: 'Imagen',
            orderable: false,
            searchable: false,
            render: function (data, type, row, meta) {
                if (data == undefined) {
                    return ''
                }
                else return '<img src="https://connect.garmin.com/' + data + '"></img>'
            }
        },
    ],
    columnDefs: [{
        "targets": "_all",
        "defaultContent": "",
    }],
    data: dataSet,
    initComplete: function () { //create filter boxes
        this.api()
            .columns([0, 2, 3]) //columns to be filtered
            // .columns([0, 2]) //columns to be filtered
            .every(function () {
                let column = this;

                // Create select element
                let select = document.createElement('select');
                select.add(new Option(''));
                let group = document.createElement('div');
                let titulo = document.createElement('p');
                let valor = column.header().textContent;
                titulo.append(valor);
                group.append(titulo);
                group.append(select);

                // column.footer().replaceChildren(select);
                column.header().replaceChildren(group);
                //select.appendTo($("filter"))
                // $("#filter").append(select)

                // Apply listener for user change in value
                select.addEventListener('change', function () {
                    var val = DataTable.util.escapeRegex(select.value);

                    column
                        // .search(val ? '^' + val + '$' : '', true, false)
                        .search(val ? val : '', false, true)
                        .draw();
                });
                // Add list of options
                dato = column.data();
                column
                    .data()
                    .flatten()
                    .unique()
                    .sort()
                    .each(function (d, j) {
                        select.add(new Option(d));
                    });
            });
    }
});

// Add event listener for adding info to separate div
table.on('click', function (e) {
    let tr = e.target.closest('tr');
    let row = table.row(tr);
    if (row.data() != undefined) $('#details').html(format(row.data()));
});