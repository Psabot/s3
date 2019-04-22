
# NFS

### Ceph RGW et NFS

Bien que la philosophie du mode RGW soit de fonctionner en mode bucket et ainsi s'affranchir de toutes les contraintes liées au FS classique, il est quand même possible d'ajouter des objets via l'interface REST de la GW et les retrouver sur le NFS. L'inverse est aussi possible. Cela permet principalement d'avoir des applications legacy ayant encore besoin d'un FS classique et en même temps des applications qui se servent directement des buckets. 
Cette solution a notamment été étudié pour pouvoir plus facilement copier les datas d'un cluster à un autre : il y aurait juste à copier les fichiers nfs d'un cluster à un autre (rsync, scp, ...).

Pour se faire, Ganesha (un NFS) et notamment son module librgw2 écrit par Ceph va permettre de faire l'abstraction du layer S3 et de le servir à l'utilisateur en tant que NFS.

![rgw-nfs-arch](http://sebastien-han.fr/blog/images/rgw-nfs-arch.png)

#### Pour l'installation avec ansible:

Pour installer le nfs avec ceph-ansible, il faut ajouter un nouveau groupe "[nfss]" avec de préférence le même host que celui de la RGW (pour éviter tout problème d'accès au noeud RGW). Ensuite, il faut simplement relancer le playbook site.yml.

#### Pour l'installation à la main:

Installation des rpm nécessaires :
``` sh
yum install nfs-ganesha-ceph nfs-ganesha-rgw ceph-radosgw
```

Modifier le fichier */etc/ganesha/ganesha.conf* :
```
[...]
# Exporting FSAL 
FSAL { 
    Name = RGW; 
    User_Id = "*user*"; 
    Access_Key_Id ="*access_key_id*"; 
    Secret_Access_Key = "*secret_access_key*"; 
  } 
} 

RGW { 
    ceph_conf = "/etc/ceph/ceph.conf"; 
    name = "client.rgw.*hostname*"; 
    cluster = "ceph"; 
}
```

Dans la partie FSAL, renseigner l'id, la clé d'access et la clé secrète d'un utilisateur s3 (*user*, *access_key_id*, *secret_access_key*).
Ou en créer un le cas échéant :
```
sudo radosgw-admin user create --admin --display-name="Admin" --email=admin@exemple.com
```

Dans la partie RGW, le hostname est à remplacer par celui de la machine où est déployée la gateway.

Redémarrer ganesha

```sh
systemctl restart nfs-ganesha.service
```

#### Faire un point de montage (Ceph ansible ET montage à la main)

```sh
mount -t nfs -o nfsvers=4.1,proto=tcp ganesha-host-name:ganesha-pseudo-path mount-point
```

Par exemple :
```sh
sudo mount -t nfs -o nfsvers=4.1,noauto,soft,sync,proto=tcp p4CephMaster13:/ /mnt/cephnfs
```

#### Difficultés rencontrées
Bien que les buckets soient visibles à la fois à travers la RGW et le NFS (la création d'un bucket via mkdir sur le NFS est visible via la RGW et inversement), il y a certains problèmes d'I/O qui empêche la bonne création d'objet en passant par le NFS.
Par exemple, un *touch* sur le NFS provoque un freeze et engendre un problème d'I/O qui empêche la bonne écriture de l'objet.
Au moment de la rédaction de cette documentation, des problèmes similaires ont été répertoriés sur github.

https://github.com/nfs-ganesha/nfs-ganesha/issues/335

https://github.com/nfs-ganesha/nfs-ganesha/issues/204

Ces problèmes dépendent de la version des binaires installés, il est donc possible que ces problèmes ne soient pas rencontrés en fonction des versions.

# Copier les objets d'un bucket à un autre

```sh
sudo yum install python34-pip
```

```sh
sudo pip3.4 install boto3
```

