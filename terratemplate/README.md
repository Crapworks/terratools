# TerraTemplate

This is a tool that allows you to use Jinja templating inside of your terraform scripts. Put the `render.py` into the same directory as your terraform scripts, install the requirements and run it.

## Quickstart / Example

```bash
$ git clone https://github.com/Crapworks/terratools.git
$ cp terratools/terratemplate/render.py /tmp/yourterraformfiles
$ pip install -r terratools/terratemplate/requirements.txt
```

Now switch to your directory containing your terraform files. Only files with the suffix `.jinja` will be rendered.

```bash
$ cd /tmp/yourterraformfiles
$ mv mykeys.tf mykeys.jinja
```

TerraState will load all your terraform scripts to check for `variable` definitions with a default value. If you set variables via `.tfvars` files, you need to add them as command line parameters to the script.

```bash
$ cat variables.tf
variable "key_count" {
    default = "1"
}

$ cat myoverwrite.tfvars
key_count = "2"
```

You can see the rendered variables if you use the `-s` switch:

```bash
$ ./render.py -s                                                                                                                                                                                                                                     ──( :) )─┘
{
  "key_count": "1"
}

$ ./render.py -s -var-file=myoverwrite.tfvars                                                                                                                                                                                                        ──( :) )─┘
{
  "key_count": "2"
}
```

This way, you can use your terraform variables in your jinja templates

```bash
$ cat mykeys.jinja
{% for count in range(key_count|int) -%}
resource "openstack_compute_keypair_v2" "user{{ count }}" {
  name = "${var.project}"
  public_key = "${file(var.public_key_path)}"
}

{% endfor %}
```

To see what is going to be rendered:

```bash
$ ./render.py -var-file=myoverwrite.tfvars --test                                                                                                                                                                                                    ──( :) )─┘
resource "openstack_compute_keypair_v2" "user0" {
  name = "${var.project}"
  public_key = "${file(var.public_key_path)}"
}

resource "openstack_compute_keypair_v2" "user1" {
  name = "${var.project}"
  public_key = "${file(var.public_key_path)}"
}
```

To finally render it to a `.tf` file, just remove the `--test` argument

```bash
$ ./render.py -var-file=myoverwrite.tfvars
$ cat  mykeys.tf                                                                                                                                                                                                                                      ──( :) )─┘
resource "openstack_compute_keypair_v2" "user0" {
  name = "${var.project}"
  public_key = "${file(var.public_key_path)}"
}

resource "openstack_compute_keypair_v2" "user1" {
  name = "${var.project}"
  public_key = "${file(var.public_key_path)}"
}
```

Have fun!
